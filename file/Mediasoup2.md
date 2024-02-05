
<!--BEGIN_DATA
{
    "create_date": "2022-03-14 18:00", 
    "modify_date": "2022-03-14 18:00", 
    "is_top": "0", 
    "summary": "Mediasoup源码分析（三）传输通道的建立<br/>Mediasoup源码分析（四）流的转发", 
    "tags": "音视频", 
    "file_name": "Mediasoup2.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://blog.csdn.net/Frederick_Fung/article/details/107105054' target='blank'>Mediasoup源码分析（三）传输通道的建立</a></p>

前面说到channel与router的建立，实际上channel是node服务器与底层C++之间信令交互的通道。transport才是router给用户推流拉流的通道，而创建完Router过后就开始创建Transport了

## 一、创建Transport

### 1、用户请求

用户想要加入房间，这时在应用层便会发送creat transport 的信令，传递给Worker

### 2、Worker——把信令传递给下一层

当Worker处理不了用户的请求时，它便把消息传递下一层，即Router

request便传递给router->HandleRequest这个函数

```cpp
default:
{
	// This may throw.
	RTC::Router* router = GetRouterFromInternal(request->internal);
	router->HandleRequest(request);
	break;
}
```

### 3、Router->HandleRequest——确定Transport的类型

进入到Router这层，系统想要create transport，由于transport是个基类，它实际上是有很多个子类

```cpp
case Channel::Request::MethodId::ROUTER_CREATE_WEBRTC_TRANSPORT:
{
	std::string transportId;
	// This may throw.
	SetNewTransportIdFromInternal(request->internal, transportId);
	// This may throw.
	auto* webRtcTransport = new RTC::WebRtcTransport(transportId, this, request->data);
	// Insert into the map.
	this->mapTransports[transportId] = webRtcTransport;
	MS_DEBUG_DEV("WebRtcTransport created [transportId:%s]", transportId.c_str());
	json data = json::object();
	webRtcTransport->FillJson(data);
	request->Accept(data);
	break;
}
```

进入SetNewTransportIdFromInternal这个函数

### 4、SetNewTransportIdFromInternal——获得TransportID

```cpp
void Router::SetNewTransportIdFromInternal(json& internal, std::string& transportId) const
{
	MS_TRACE();
	auto jsonTransportIdIt = internal.find("transportId");
	if (jsonTransportIdIt == internal.end() || !jsonTransportIdIt->is_string())
		MS_THROW_ERROR("missing internal.transportId");
	transportId.assign(jsonTransportIdIt->get<std::string>());
	if (this->mapTransports.find(transportId) != this->mapTransports.end())
		MS_THROW_ERROR("a Transport with same transportId already exists");
}
```

**这段代码就是从internal中搜索transport的ID，找到ID后返回**

回到Router后，执行`auto* webRtcTransport = new RTC::WebRtcTransport(transportId,this, request->data);` 接着进入**RTC::WebRtcTransport**

### 5、RTC::WebRtcTransport——创建Transport

从源码来看，这个构造函数的前半部分是解析json数据，它包括

  * enableUdp
  * enableTcp
  * preferUdp
  * preferTcp
  * listenIps
  * 等等

```cpp
WebRtcTransport::WebRtcTransp ort(const std::string& id, RTC::Transport::Listener* listener, json& data)
  : RTC::Transport::Transport(id, listener, data)
{
  MS_TRACE();

  bool enableUdp{ true };
  auto jsonEnableUdpIt = data.find("enableUdp");

  if (jsonEnableUdpIt != data.end())
  {
    if (!jsonEnableUdpIt->is_boolean())
      MS_THROW_TYPE_ERROR("wrong enableUdp (not a boolean)");

    enableUdp = jsonEnableUdpIt->get<bool>();
  }

  bool enableTcp{ false };
  auto jsonEnableTcpIt = data.find("enableTcp");

  if (jsonEnableTcpIt != data.end())
  {
    if (!jsonEnableTcpIt->is_boolean())
      MS_THROW_TYPE_ERROR("wrong enableTcp (not a boolean)");

    enableTcp = jsonEnableTcpIt->get<bool>();
  }

  bool preferUdp{ false };
  auto jsonPreferUdpIt = data.find("preferUdp");

  if (jsonPreferUdpIt != data.end())
  {
    if (!jsonPreferUdpIt->is_boolean())
      MS_THROW_TYPE_ERROR("wrong preferUdp (not a boolean)");

    preferUdp = jsonPreferUdpIt->get<bool>();
  }

  bool preferTcp{ false };
  auto jsonPreferTcpIt = data.find("preferTcp");

  if (jsonPreferTcpIt != data.end())
  {
    if (!jsonPreferTcpIt->is_boolean())
      MS_THROW_TYPE_ERROR("wrong preferTcp (not a boolean)");

    preferTcp = jsonPreferTcpIt->get<bool>();
  }

  auto jsonListenIpsIt = data.find("listenIps");

  if (jsonListenIpsIt == data.end())
    MS_THROW_TYPE_ERROR("missing listenIps");
  else if (!jsonListenIpsIt->is_array())
    MS_THROW_TYPE_ERROR("wrong listenIps (not an array)");
  else if (jsonListenIpsIt->empty())
    MS_THROW_TYPE_ERROR("wrong listenIps (empty array)");
  else if (jsonListenIpsIt->size() > 8)
    MS_THROW_TYPE_ERROR("wrong listenIps (too many IPs)");

  std::vector<ListenIp> listenIps(jsonListenIpsIt->size());

  for (size_t i{ 0 }; i < jsonListenIpsIt->size(); ++i)
  {
    auto& jsonListenIp = (*jsonListenIpsIt)[i];
    auto& listenIp     = listenIps[i];

    if (!jsonListenIp.is_object())
      MS_THROW_TYPE_ERROR("wrong listenIp (not an object)");

    auto jsonIpIt = jsonListenIp.find("ip");

    if (jsonIpIt == jsonListenIp.end())
      MS_THROW_TYPE_ERROR("missing listenIp.ip");
    else if (!jsonIpIt->is_string())
      MS_THROW_TYPE_ERROR("wrong listenIp.ip (not an string");

    listenIp.ip.assign(jsonIpIt->get<std::string>());

    // This may throw.
    Utils::IP::NormalizeIp(listenIp.ip);

    auto jsonAnnouncedIpIt = jsonListenIp.find("announcedIp");

    if (jsonAnnouncedIpIt != jsonListenIp.end())
    {
      if (!jsonAnnouncedIpIt->is_string())
        MS_THROW_TYPE_ERROR("wrong listenIp.announcedIp (not an string)");

      listenIp.announcedIp.assign(jsonAnnouncedIpIt->get<std::string>());
    }
  }
```

解析完数据后，后半部分通过ip生成服务端的candidate，利用listenIp : listenIps来控制，有candidate就有权限

ICE通过IceServer创建，GetRandomString(16)，就是产生一个16位的随机值，32就是32位的随机值

进入IceServer的构造函数可以发现，当有用户连接这个Transport时，将会生成16位的用户名和32位的密码

```cpp
try
  {
    uint16_t iceLocalPreferenceDecrement{ 0 };

    if (enableUdp && enableTcp) 
      this->iceCandidates.reserve(2 * jsonListenIpsIt->size());
    else
      this->iceCandidates.reserve(jsonListenIpsIt->size());

    for (auto& listenIp : listenIps)
    {
      if (enableUdp)
      {
        uint16_t iceLocalPreference =
          IceCandidateDefaultLocalPriority - iceLocalPreferenceDecrement;

        if (preferUdp)
          iceLocalPreference += 1000;

        uint32_t icePriority = generateIceCandidatePriority(iceLocalPreference);

        // This may throw.
        auto* udpSocket = new RTC::UdpSocket(this, listenIp.ip);

        this->udpSockets[udpSocket] = listenIp.announcedIp;

        if (listenIp.announcedIp.empty())
          this->iceCandidates.emplace_back(udpSocket, icePriority);
        else
          this->iceCandidates.emplace_back(udpSocket, icePriority, listenIp.announcedIp);
      }

      if (enableTcp)
      {
        uint16_t iceLocalPreference =
          IceCandidateDefaultLocalPriority - iceLocalPreferenceDecrement;

        if (preferTcp)
          iceLocalPreference += 1000;

        uint32_t icePriority = generateIceCandidatePriority(iceLocalPreference);

        // This may throw.
        auto* tcpServer = new RTC::TcpServer(this, this, listenIp.ip);

        this->tcpServers[tcpServer] = listenIp.announcedIp;

        if (listenIp.announcedIp.empty())
          this->iceCandidates.emplace_back(tcpServer, icePriority);
        else
          this->iceCandidates.emplace_back(tcpServer, icePriority, listenIp.announcedIp);
      }

      // Decrement initial ICE local preference for next IP.
      iceLocalPreferenceDecrement += 100;
    }

    // Create a ICE server.
    this->iceServer = new RTC::IceServer(
      this, Utils::Crypto::GetRandomString(16), Utils::Crypto::GetRandomString(32));

    // Create a DTLS transport.
    this->dtlsTransport = new RTC::DtlsTransport(this);
  }
  catch (const MediaSoupError& error)
  {
    // Must delete everything since the destructor won't be called.

    delete this->dtlsTransport;
    this->dtlsTransport = nullptr;

    delete this->iceServer;
    this->iceServer = nullptr;

    for (auto& kv : this->udpSockets)
    {
      auto* udpSocket = kv.first;

      delete udpSocket;
    }
    this->udpSockets.clear();

    for (auto& kv : this->tcpServers)
    {
      auto* tcpServer = kv.first;

      delete tcpServer;
    }
    this->tcpServers.clear();

    this->iceCandidates.clear();

    throw;
  }
}
```

它还创建了一个DTLS transport 的对象

#### 5.1、DtlsTransport

在DtlsTransport中，首先创建了一个SSL对象，通过sslCtx上下文，因为在上下文中是有证书和私钥的

SSL就相当于一个连接，类似socket。SSL本身也有一些数据，创建的时候通过this能够获取到这些参数

然后通过创建BIO（Buffer IO）来形成两个管道，通过管道分别实现接、收数据的功能，再通过`SSL_set_bio(this->ssl, this->sslBioFromNetwork, this->sslBioToNetwork);`完成SSL对两个管道的绑定

接着还设置timer，用来控制DTLS握手的时间，超时后会做其他处理

```cpp
DtlsTransport::DtlsTransport(Listener* listener) : listener(listener)
{
  MS_TRACE();

  /* Set SSL. */

  this->ssl = SSL_new(DtlsTransport::sslCtx);

  if (!this->ssl)
  {
    LOG_OPENSSL_ERROR("SSL_new() failed");

    goto error;
  }

  // Set this as custom data.
  SSL_set_ex_data(this->ssl, 0, static_cast<void*>(this));

  this->sslBioFromNetwork = BIO_new(BIO_s_mem());

  if (!this->sslBioFromNetwork)
  {
    LOG_OPENSSL_ERROR("BIO_new() failed");

    SSL_free(this->ssl);

    goto error;
  }

  this->sslBioToNetwork = BIO_new(BIO_s_mem());

  if (!this->sslBioToNetwork)
  {
    LOG_OPENSSL_ERROR("BIO_new() failed");

    BIO_free(this->sslBioFromNetwork);
    SSL_free(this->ssl);

    goto error;
  }

  SSL_set_bio(this->ssl, this->sslBioFromNetwork, this->sslBioToNetwork);

  // Set the MTU so that we don't send packets that are too large with no fragmentation.
  SSL_set_mtu(this->ssl, DtlsMtu);
  DTLS_set_link_mtu(this->ssl, DtlsMtu);

  // Set callback handler for setting DTLS timer interval.
  DTLS_set_timer_cb(this->ssl, onSslDtlsTimer);

  // Set the DTLS timer.
  this->timer = new Timer(this);

  return;

error:

  // NOTE: At this point SSL_set_bio() was not called so we must free BIOs as
  // well.
  if (this->sslBioFromNetwork)
    BIO_free(this->sslBioFromNetwork);

  if (this->sslBioToNetwork)
    BIO_free(this->sslBioToNetwork);

  if (this->ssl)
    SSL_free(this->ssl);

  // NOTE: If this is not catched by the caller the program will abort, but
  // this should never happen.
  MS_THROW_ERROR("DtlsTransport instance creation failed");
}
```

### 6、default——处理非CreateTransport类型的信令请求

```cpp
default:
{
	// This may throw.
	RTC::Transport* transport = GetTransportFromInternal(request->internal);
	transport->HandleRequest(request);
	break;
}
```

接下来进入HandleRequest，本文跳转至 第二章第2节

## 二、建立connect连接

### 1、main.cpp——各模块的初始化

首先在main.cpp中各对与connect相关的所有模块进行了初始化

```cpp
// Initialize static stuff.
DepOpenSSL::ClassInit();
DepLibSRTP::ClassInit();
DepUsrSCTP::ClassInit();
DepLibWebRTC::ClassInit();
Utils::Crypto::ClassInit();
RTC::DtlsTransport::ClassInit();
RTC::SrtpSession::ClassInit();
Channel::Notifier::ClassInit(channel);
PayloadChannel::Notifier::ClassInit(payloadChannel);
```

#### 1.1、DepOpenSSL——加密算法随机数的产生

```cpp
void DepOpenSSL::ClassInit()
{
	MS_TRACE();
	MS_DEBUG_TAG(info, "openssl version: \"%s\"", OpenSSL_version(OPENSSL_VERSION));
	// Initialize some crypto stuff.
	RAND_poll();
}
```

这部分主要是对加密算法的随机数的生成

#### 1.2、DepLibSRTP——初始化srtp

```cpp
void DepLibSRTP::ClassInit()
{
	MS_TRACE();
	MS_DEBUG_TAG(info, "libsrtp version: \"%s\"", srtp_get_version_string());
	srtp_err_status_t err = srtp_init();
	if (DepLibSRTP::IsError(err))
		MS_THROW_ERROR("srtp_init() failed: %s", DepLibSRTP::GetErrorString(err));
}
```

这部分调用了srtp_init 这个API，这个API的返回值对后面Session的初始化有着重要的作用

#### 1.3、DepUsrSCTP

```cpp
void DepUsrSCTP::ClassInit()
{
	MS_TRACE();
	MS_DEBUG_TAG(info, "usrsctp");
	usrsctp_init_nothreads(0, onSendSctpData, sctpDebug);
	// Disable explicit congestion notifications (ecn).
	usrsctp_sysctl_set_sctp_ecn_enable(0);
#ifdef SCTP_DEBUG
	usrsctp_sysctl_set_sctp_debug_on(SCTP_DEBUG_ALL);
#endif
	DepUsrSCTP::checker = new DepUsrSCTP::Checker();
}
```

#### 1.4、Utils::Crypto——产生`ice_ufrag、ice_password`的算法

```cpp
void Crypto::ClassInit()
{
	MS_TRACE();
	// Init the vrypto seed with a random number taken from the address
	// of the seed variable itself (which is random).
	Crypto::seed = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(std::addressof(Crypto::seed)));
	// Create an OpenSSL HMAC_CTX context for HMAC SHA1 calculation.
	Crypto::hmacSha1Ctx = HMAC_CTX_new();
}
```

创建了Crypto的种子，使用的算法是HMAC，其中H代表的是hash哈希

#### 1.5、RTC::DtlsTransport——证书和私钥

```cpp
void DtlsTransport::ClassInit()
{
	MS_TRACE();
	// Generate a X509 certificate and private key (unless PEM files are provided).
	if (
	  Settings::configuration.dtlsCertificateFile.empty() ||
	  Settings::configuration.dtlsPrivateKeyFile.empty())
	{
		GenerateCertificateAndPrivateKey();
	}
	else
	{
		ReadCertificateAndPrivateKeyFromFiles();
	}
	// Create a global SSL_CTX.
	CreateSslCtx();
	// Generate certificate fingerprints.
	GenerateFingerprints();
}
```

在代码中首先判断有没有证书和私钥，若没有便通过 GenerateCertificateAndPrivateKey 这个函数产生一个证书和私钥

##### 1.5.1、GenerateCertificateAndPrivateKey——产生证书和私钥

```cpp
void DtlsTransport::GenerateCertificateAndPrivateKey()
{
  MS_TRACE();

  int ret{ 0 };
  EC_KEY* ecKey{ nullptr };
  X509_NAME* certName{ nullptr };
  std::string subject =
    std::string("mediasoup") + std::to_string(Utils::Crypto::GetRandomUInt(100000, 999999));

  // Create key with curve.
  ecKey = EC_KEY_new_by_curve_name(NID_X9_62_prime256v1);

  if (ecKey == nullptr)
  {
    LOG_OPENSSL_ERROR("EC_KEY_new_by_curve_name() failed");

    goto error;
  }

  EC_KEY_set_asn1_flag(ecKey, OPENSSL_EC_NAMED_CURVE);

  // NOTE: This can take some time.
  ret = EC_KEY_generate_key(ecKey);

  if (ret == 0)
  {
    LOG_OPENSSL_ERROR("EC_KEY_generate_key() failed");

    goto error;
  }

  // Create a private key object.
  DtlsTransport::privateKey = EVP_PKEY_new();

  if (!DtlsTransport::privateKey)
  {
    LOG_OPENSSL_ERROR("EVP_PKEY_new() failed");

    goto error;
  }

  // NOLINTNEXTLINE(cppcoreguidelines-pro-type-cstyle-cast)
  ret = EVP_PKEY_assign_EC_KEY(DtlsTransport::privateKey, ecKey);

  if (ret == 0)
  {
    LOG_OPENSSL_ERROR("EVP_PKEY_assign_EC_KEY() failed");

    goto error;
  }

  // The EC key now belongs to the private key, so don't clean it up separately.
  ecKey = nullptr;

  // Create the X509 certificate.
  DtlsTransport::certificate = X509_new();

  if (!DtlsTransport::certificate)
  {
    LOG_OPENSSL_ERROR("X509_new() failed");

    goto error;
  }

  // Set version 3 (note that 0 means version 1).
  X509_set_version(DtlsTransport::certificate, 2);

  // Set serial number (avoid default 0).
  ASN1_INTEGER_set(
    X509_get_serialNumber(DtlsTransport::certificate),
    static_cast<uint64_t>(Utils::Crypto::GetRandomUInt(1000000, 9999999)));

  // Set valid period.
  X509_gmtime_adj(X509_get_notBefore(DtlsTransport::certificate), -315360000); // -10 years.
  X509_gmtime_adj(X509_get_notAfter(DtlsTransport::certificate), 315360000);   // 10 years.

  // Set the public key for the certificate using the key.
  ret = X509_set_pubkey(DtlsTransport::certificate, DtlsTransport::privateKey);

  if (ret == 0)
  {
    LOG_OPENSSL_ERROR("X509_set_pubkey() failed");

    goto error;
  }

  // Set certificate fields.
  certName = X509_get_subject_name(DtlsTransport::certificate);

  if (!certName)
  {
    LOG_OPENSSL_ERROR("X509_get_subject_name() failed");

    goto error;
  }

  X509_NAME_add_entry_by_txt(
    certName, "O", MBSTRING_ASC, reinterpret_cast<const uint8_t*>(subject.c_str()), -1, -1, 0);
  X509_NAME_add_entry_by_txt(
    certName, "CN", MBSTRING_ASC, reinterpret_cast<const uint8_t*>(subject.c_str()), -1, -1, 0);

  // It is self-signed so set the issuer name to be the same as the subject.
  ret = X509_set_issuer_name(DtlsTransport::certificate, certName);

  if (ret == 0)
  {
    LOG_OPENSSL_ERROR("X509_set_issuer_name() failed");

    goto error;
  }

  // Sign the certificate with its own private key.
  ret = X509_sign(DtlsTransport::certificate, DtlsTransport::privateKey, EVP_sha1());

  if (ret == 0)
  {
    LOG_OPENSSL_ERROR("X509_sign() failed");

    goto error;
  }

  return;

error:

  if (ecKey)
    EC_KEY_free(ecKey);

  if (DtlsTransport::privateKey)
    EVP_PKEY_free(DtlsTransport::privateKey); // NOTE: This also frees the EC key.

  if (DtlsTransport::certificate)
    X509_free(DtlsTransport::certificate);

  MS_THROW_ERROR("DTLS certificate and private key generation failed");
}
```

这部分代码一连串的if语句，调用API创建了证书，生成其版本、序列号等等

```cpp
// Create the X509 certificate.
DtlsTransport::certificate = X509_new();
```

##### 1.5.2、ReadCertificateAndPrivateKeyFromFiles——已有私钥和证书

若有自己的证书和API，则进入这个函数

函数体用的开始是用文件类型打开，接着调用API读取证书和私钥

```cpp
void DtlsTransport::ReadCertificateAndPrivateKeyFromFiles()
{
  MS_TRACE();

  FILE* file{ nullptr };

  file = fopen(Settings::configuration.dtlsCertificateFile.c_str(), "r");

  if (!file)
  {
    MS_ERROR("error reading DTLS certificate file: %s", std::strerror(errno));

    goto error;
  }

  DtlsTransport::certificate = PEM_read_X509(file, nullptr, nullptr, nullptr);

  if (!DtlsTransport::certificate)
  {
    LOG_OPENSSL_ERROR("PEM_read_X509() failed");

    goto error;
  }

  fclose(file);

  file = fopen(Settings::configuration.dtlsPrivateKeyFile.c_str(), "r");

  if (!file)
  {
    MS_ERROR("error reading DTLS private key file: %s", std::strerror(errno));

    goto error;
  }

  DtlsTransport::privateKey = PEM_read_PrivateKey(file, nullptr, nullptr, nullptr);

  if (!DtlsTransport::privateKey)
  {
    LOG_OPENSSL_ERROR("PEM_read_PrivateKey() failed");

    goto error;
  }

  fclose(file);

  return;

error:

  MS_THROW_ERROR("error reading DTLS certificate and private key PEM files");
}
```

##### 1.5.3、CreateSslCtx——创建SSL上下文

拿到证书和私钥后，将会创建一个SSL上下文。首先对Dtls的版本做了判断

```cpp
// Both DTLS 1.0 and 1.2 (requires OpenSSL >= 1.1.0).
DtlsTransport::sslCtx = SSL_CTX_new(DTLS_method());
```

然后会把证书与上下文绑定

```cpp
ret = SSL_CTX_use_certificate(DtlsTransport::sslCtx, DtlsTransport::certificate);
```

key也会与上下文绑定

```cpp
ret = SSL_CTX_use_PrivateKey(DtlsTransport::sslCtx, DtlsTransport::privateKey);
```

接着对key做了检查，设置了一些选项

```cpp
// Set options.
SSL_CTX_set_options(
  DtlsTransport::sslCtx,
  SSL_OP_CIPHER_SERVER_PREFERENCE | SSL_OP_NO_TICKET | SSL_OP_SINGLE_ECDH_USE |
    SSL_OP_NO_QUERY_MTU);
```

设置ciphers，它是一个密语的套件，具体是哪些加密算法就是通过它来设置的，用一个字符串来描述

```cpp
// Set ciphers.
ret = SSL_CTX_set_cipher_list(
	  DtlsTransport::sslCtx, "DEFAULT:!NULL:!aNULL:!SHA256:!SHA384:!aECDH:!AESGCM+AES256:!aPSK");
```

除此之外，Dtls使用srtp来加密解密。这个for循环通过对srtpCryptoSuites的遍历，累加在dtlsSrtpCryptoSuites后面，然后利用`SSL_CTX_set_tlsext_use_srtp`这个API设置进去

```cpp
// Set the "use_srtp" DTLS extension.
for (auto it = DtlsTransport::srtpCryptoSuites.begin();
     it != DtlsTransport::srtpCryptoSuites.end();
     ++it)
{
	if (it != DtlsTransport::srtpCryptoSuites.begin())
		dtlsSrtpCryptoSuites += ":";
	SrtpCryptoSuiteMapEntry* cryptoSuiteEntry = std::addressof(*it);
	dtlsSrtpCryptoSuites += cryptoSuiteEntry->name;
}
```

##### 1.5.5、GenerateFingerprints()——生成指纹

```cpp
void DtlsTransport::GenerateFingerprints()
{
  MS_TRACE();

  for (auto& kv : DtlsTransport::string2FingerprintAlgorithm)
  {
    const std::string& algorithmString = kv.first;
    FingerprintAlgorithm algorithm     = kv.second;
    uint8_t binaryFingerprint[EVP_MAX_MD_SIZE];
    unsigned int size{ 0 };
    char hexFingerprint[(EVP_MAX_MD_SIZE * 3) + 1];
    const EVP_MD* hashFunction;
    int ret;

    switch (algorithm)
    {
      case FingerprintAlgorithm::SHA1:
        hashFunction = EVP_sha1();
        break;

      case FingerprintAlgorithm::SHA224:
        hashFunction = EVP_sha224();
        break;

      case FingerprintAlgorithm::SHA256:
        hashFunction = EVP_sha256();
        break;

      case FingerprintAlgorithm::SHA384:
        hashFunction = EVP_sha384();
        break;

      case FingerprintAlgorithm::SHA512:
        hashFunction = EVP_sha512();
        break;

      default:
        MS_THROW_ERROR("unknown algorithm");
    }

    ret = X509_digest(DtlsTransport::certificate, hashFunction, binaryFingerprint, &size);

    if (ret == 0)
    {
      MS_ERROR("X509_digest() failed");
      MS_THROW_ERROR("Fingerprints generation failed");
    }

    // Convert to hexadecimal format in uppercase with colons.
    for (unsigned int i{ 0 }; i < size; ++i)
    {
      std::sprintf(hexFingerprint + (i * 3), "%.2X:", binaryFingerprint[i]);
    }
    hexFingerprint[(size * 3) - 1] = '\0';

    MS_DEBUG_TAG(dtls, "%-7s fingerprint: %s", algorithmString.c_str(), hexFingerprint);

    // Store it in the vector.
    DtlsTransport::Fingerprint fingerprint;

    fingerprint.algorithm = DtlsTransport::GetFingerprintAlgorithm(algorithmString);
    fingerprint.value     = hexFingerprint;

    DtlsTransport::localFingerprints.push_back(fingerprint);
  }
}
```

指纹是通过证书来产生的，这个函数体内定义了多种产生指纹的算法，如

  * SHA1
  * SHA224
  * SHA256
  * SHA384
  * SHA512

对于每种不同的算法它都有对应的函数，然后通过`ret = X509_digest(DtlsTransport::certificate, hashFunction, binaryFingerprint, &size);`这个API计算证书的指纹，结果存放在binaryFingerprint里

接着把binaryFingerprint转化为十六进制的格式`std::sprintf(hexFingerprint + (i * 3), "%.2X:", binaryFingerprint[i]);`

完成后把结果的值存放进fingerprint.value，使用的算法是fingerprint.algorithm

最后再把fingerprint这个对象存放进localFingerprints

这样指纹便创建好了

#### 1.6、RTC::SrtpSession——定义处理不同事件的方法

```cpp
void SrtpSession::ClassInit()
{
	// Set libsrtp event handler.
	srtp_err_status_t err =
	  srtp_install_event_handler(static_cast<srtp_event_handler_func_t*>(OnSrtpEvent));
	if (DepLibSRTP::IsError(err))
	{
		MS_THROW_ERROR("srtp_install_event_handler() failed: %s", DepLibSRTP::GetErrorString(err));
	}
}
```

Session这块代码主要是在OnSrtpEvent()这个函数中定义了对不同事件的处理

##### 1.6.1、OnSrtpEvent()——打印事件异常的信息

```cpp
void SrtpSession::OnSrtpEvent(srtp_event_data_t* data)
{
	MS_TRACE();
	switch (data->event)
	{
		case event_ssrc_collision:
			MS_WARN_TAG(srtp, "SSRC collision occurred");
			break;
		case event_key_soft_limit:
			MS_WARN_TAG(srtp, "stream reached the soft key usage limit and will expire soon");
			break;
		case event_key_hard_limit:
			MS_WARN_TAG(srtp, "stream reached the hard key usage limit and has expired");
			break;
		case event_packet_index_limit:
			MS_WARN_TAG(srtp, "stream reached the hard packet limit (2^48 packets)");
			break;
	}
}
```

如ssrc冲突、软件硬件的限制，主要是打印错误信息

#### 1.7、Channel::Notifier

```cpp
void Notifier::ClassInit(Channel::UnixStreamSocket* channel)
{
	MS_TRACE();
	Notifier::channel = channel;
}
```

#### 1.8、PayloadChannel::Notifier

```cpp
void Notifier::ClassInit(PayloadChannel::UnixStreamSocket* payloadChannel)
{
	MS_TRACE();
	Notifier::payloadChannel = payloadChannel;
}
```

### 2、WebRtcTransport

当以上准备工作做好后了，WebRtcTransport要给客户端返回一个数据data，进入WebRtcTransport::FillJson

#### 2.1、WebRtcTransport::FillJson——配置ICE、dtls参数信息以json传给应用层

```cpp
// Add iceRole (we are always "controlled").
jsonObject["iceRole"] = "controlled";
// Add iceParameters.
jsonObject["iceParameters"] = json::object();
auto jsonIceParametersIt    = jsonObject.find("iceParameters");
(*jsonIceParametersIt)["usernameFragment"] = this->iceServer->GetUsernameFragment();
(*jsonIceParametersIt)["password"]         = this->iceServer->GetPassword();
(*jsonIceParametersIt)["iceLite"]          = true;
```

在FillJson里，iceRole总是设为被控制端

当创建一个transport时，会收到从服务端返回的ice_ufrag和ice_password

iceLite是指使用的ICE不是完整的ICE，而是其中部分ICE协议

```cpp
// Add iceCandidates.
jsonObject["iceCandidates"] = json::array();
auto jsonIceCandidatesIt    = jsonObject.find("iceCandidates");
for (size_t i{ 0 }; i < this->iceCandidates.size(); ++i)
{
	jsonIceCandidatesIt->emplace_back(json::value_t::object);
	auto& jsonEntry    = (*jsonIceCandidatesIt)[i];
	auto& iceCandidate = this->iceCandidates[i];
	iceCandidate.FillJson(jsonEntry);
}
```

我们还从服务端收到了许多IP，它们形成了candidate，然后把这些candidate组成数组放入json中

```cpp
// Add iceState.
switch (this->iceServer->GetState())
{
	case RTC::IceServer::IceState::NEW:
		jsonObject["iceState"] = "new";
		break;
	case RTC::IceServer::IceState::CONNECTED:
		jsonObject["iceState"] = "connected";
		break;
	case RTC::IceServer::IceState::COMPLETED:
		jsonObject["iceState"] = "completed";
		break;
	case RTC::IceServer::IceState::DISCONNECTED:
		jsonObject["iceState"] = "disconnected";
		break;
}
```

ICE的状态，一般为new

```cpp
// Add dtlsParameters.
jsonObject["dtlsParameters"] = json::object();
auto jsonDtlsParametersIt    = jsonObject.find("dtlsParameters");

// Add dtlsParameters.fingerprints.
(*jsonDtlsParametersIt)["fingerprints"] = json::array();
auto jsonDtlsParametersFingerprintsIt   = jsonDtlsParametersIt->find("fingerprints");
auto& fingerprints                      = this->dtlsTransport->GetLocalFingerprints();

for (size_t i{ 0 }; i < fingerprints.size(); ++i)
{
	jsonDtlsParametersFingerprintsIt->emplace_back(json::value_t::object);
	auto& jsonEntry   = (*jsonDtlsParametersFingerprintsIt)[i];
	auto& fingerprint = fingerprints[i];
	jsonEntry["algorithm"] =
	  RTC::DtlsTransport::GetFingerprintAlgorithmString(fingerprint.algorithm);
	jsonEntry["value"] = fingerprint.value;
}
```

dtls的参数，其中最重要的是fingerprint，它是一组数据（因为用了不同的加密算法），然后形成一个数组把它塞入fingerprints，同时传给客户端，客户端就拿到了各种指纹和证书了

```cpp
// Add dtlsParameters.role.
	switch (this->dtlsRole)
	{
		case RTC::DtlsTransport::Role::NONE:
			(*jsonDtlsParametersIt)["role"] = "none";
			break;
		case RTC::DtlsTransport::Role::AUTO:
			(*jsonDtlsParametersIt)["role"] = "auto";
			break;
		case RTC::DtlsTransport::Role::CLIENT:
			(*jsonDtlsParametersIt)["role"] = "client";
			break;
		case RTC::DtlsTransport::Role::SERVER:
			(*jsonDtlsParametersIt)["role"] = "server";
			break;
	}

	// Add dtlsState.
	switch (this->dtlsTransport->GetState())
	{
		case RTC::DtlsTransport::DtlsState::NEW:
			jsonObject["dtlsState"] = "new";
			break;
		case RTC::DtlsTransport::DtlsState::CONNECTING:
			jsonObject["dtlsState"] = "connecting";
			break;
		case RTC::DtlsTransport::DtlsState::CONNECTED:
			jsonObject["dtlsState"] = "connected";
			break;
		case RTC::DtlsTransport::DtlsState::FAILED:
			jsonObject["dtlsState"] = "failed";
			break;
		case RTC::DtlsTransport::DtlsState::CLOSED:
			jsonObject["dtlsState"] = "closed";
			break;
	}
}
```

除此之外还有dtls的角色和传输状态

以上所有信息都会一起打包传给应用层，应用层就拿到了服务端的信息，然后就可以进行验证

#### 2.2、WebRtcTransport::HandleRequest——给客户端证书的相关信息

```cpp
case Channel::Request::MethodId::TRANSPORT_CONNECT:
{
  // Ensure this method is not called twice.
  if (this->connectCalled)
    MS_THROW_ERROR("connect() already called");

  RTC::DtlsTransport::Fingerprint dtlsRemoteFingerprint;
  RTC::DtlsTransport::Role dtlsRemoteRole;

  auto jsonDtlsParametersIt = request->data.find("dtlsParameters");

  if (jsonDtlsParametersIt == request->data.end() || !jsonDtlsParametersIt->is_object())
    MS_THROW_TYPE_ERROR("missing dtlsParameters");

  auto jsonFingerprintsIt = jsonDtlsParametersIt->find("fingerprints");

  if (jsonFingerprintsIt == jsonDtlsParametersIt->end() || !jsonFingerprintsIt->is_array())
    MS_THROW_TYPE_ERROR("missing dtlsParameters.fingerprints");

  // NOTE: Just take the first fingerprint.
  for (auto& jsonFingerprint : *jsonFingerprintsIt)
  {
    if (!jsonFingerprint.is_object())
      MS_THROW_TYPE_ERROR("wrong entry in dtlsParameters.fingerprints (not an object)");

    auto jsonAlgorithmIt = jsonFingerprint.find("algorithm");

    if (jsonAlgorithmIt == jsonFingerprint.end())
      MS_THROW_TYPE_ERROR("missing fingerprint.algorithm");
    else if (!jsonAlgorithmIt->is_string())
      MS_THROW_TYPE_ERROR("wrong fingerprint.algorithm (not a string)");

    dtlsRemoteFingerprint.algorithm =
      RTC::DtlsTransport::GetFingerprintAlgorithm(jsonAlgorithmIt->get<std::string>());

    if (dtlsRemoteFingerprint.algorithm == RTC::DtlsTransport::FingerprintAlgorithm::NONE)
      MS_THROW_TYPE_ERROR("invalid fingerprint.algorithm value");

    auto jsonValueIt = jsonFingerprint.find("value");

    if (jsonValueIt == jsonFingerprint.end())
      MS_THROW_TYPE_ERROR("missing fingerprint.value");
    else if (!jsonValueIt->is_string())
      MS_THROW_TYPE_ERROR("wrong fingerprint.value (not a string)");

    dtlsRemoteFingerprint.value = jsonValueIt->get<std::string>();

    // Just use the first fingerprint.
    break;
  }

  auto jsonRoleIt = jsonDtlsParametersIt->find("role");

  if (jsonRoleIt != jsonDtlsParametersIt->end())
  {
    if (!jsonRoleIt->is_string())
      MS_THROW_TYPE_ERROR("wrong dtlsParameters.role (not a string)");

    dtlsRemoteRole = RTC::DtlsTransport::StringToRole(jsonRoleIt->get<std::string>());

    if (dtlsRemoteRole == RTC::DtlsTransport::Role::NONE)
      MS_THROW_TYPE_ERROR("invalid dtlsParameters.role value");
  }
  else
  {
    dtlsRemoteRole = RTC::DtlsTransport::Role::AUTO;
  }

  // Set local DTLS role.
  switch (dtlsRemoteRole)
  {
    case RTC::DtlsTransport::Role::CLIENT:
    {
      this->dtlsRole = RTC::DtlsTransport::Role::SERVER;

      break;
    }
    // If the peer has role "auto" we become "client" since we are ICE controlled.
    case RTC::DtlsTransport::Role::SERVER:
    case RTC::DtlsTransport::Role::AUTO:
    {
      this->dtlsRole = RTC::DtlsTransport::Role::CLIENT;

      break;
    }
    case RTC::DtlsTransport::Role::NONE:
    {
      MS_THROW_TYPE_ERROR("invalid remote DTLS role");
    }
  }

  this->connectCalled = true;

  // Pass the remote fingerprint to the DTLS transport.
  if (this->dtlsTransport->SetRemoteFingerprint(dtlsRemoteFingerprint))
  {
    // If everything is fine, we may run the DTLS transport if ready.
    MayRunDtlsTransport();
  }

  // Tell the caller about the selected local DTLS role.
  json data = json::object();

  switch (this->dtlsRole)
  {
    case RTC::DtlsTransport::Role::CLIENT:
      data["dtlsLocalRole"] = "client";
      break;

    case RTC::DtlsTransport::Role::SERVER:
      data["dtlsLocalRole"] = "server";
      break;

    default:
      MS_ABORT("invalid local DTLS role");
  }

  request->Accept(data);

  break;
}
```

当收到客户端发送过来的TRANSPORT_CONNECT请求时，会创建远端的dtlsRemoteFingerprint和远端的dtlsRemoteRole，然后在for循环中找寻dtlsRemoteFingerprint.algorithm所使用的算法，以及对应的值jsonValueIt

这样客户端就拿到了证书的指纹、证书的值以及使用的算法

这些都配置好后便进入MayRunDtlsTransport()

#### 2.3、MayRunDtlsTransport()——dtls角色的选择

这个函数会根据Dtls的角色来进行不同的操作

```cpp
void WebRtcTransport::MayRunDtlsTransport()
{
  MS_TRACE();

  // Do nothing if we have the same local DTLS role as the DTLS transport.
  // NOTE: local role in DTLS transport can be NONE, but not ours.
  if (this->dtlsTransport->GetLocalRole() == this->dtlsRole)
    return;

  // Check our local DTLS role.
  switch (this->dtlsRole)
  {
    // If still 'auto' then transition to 'server' if ICE is 'connected' or
    // 'completed'.
    case RTC::DtlsTransport::Role::AUTO:
    {
      // clang-format off
      if (
        this->iceServer->GetState() == RTC::IceServer::IceState::CONNECTED ||
        this->iceServer->GetState() == RTC::IceServer::IceState::COMPLETED
      )
      // clang-format on
      {
        MS_DEBUG_TAG(
          dtls, "transition from DTLS local role 'auto' to 'server' and running DTLS transport");

        this->dtlsRole = RTC::DtlsTransport::Role::SERVER;
        this->dtlsTransport->Run(RTC::DtlsTransport::Role::SERVER);
      }

      break;
    }

    // 'client' is only set if a 'connect' request was previously called with
    // remote DTLS role 'server'.
    //
    // If 'client' then wait for ICE to be 'completed' (got USE-CANDIDATE).
    //
    // NOTE: This is the theory, however let's be more flexible as told here:
    //   https://bugs.chromium.org/p/webrtc/issues/detail?id=3661
    case RTC::DtlsTransport::Role::CLIENT:
    {
      // clang-format off
      if (
        this->iceServer->GetState() == RTC::IceServer::IceState::CONNECTED ||
        this->iceServer->GetState() == RTC::IceServer::IceState::COMPLETED
      )
      // clang-format on
      {
        MS_DEBUG_TAG(dtls, "running DTLS transport in local role 'client'");

        this->dtlsTransport->Run(RTC::DtlsTransport::Role::CLIENT);
      }

      break;
    }

    // If 'server' then run the DTLS transport if ICE is 'connected' (not yet
    // USE-CANDIDATE) or 'completed'.
    case RTC::DtlsTransport::Role::SERVER:
    {
      // clang-format off
      if (
        this->iceServer->GetState() == RTC::IceServer::IceState::CONNECTED ||
        this->iceServer->GetState() == RTC::IceServer::IceState::COMPLETED
      )
      // clang-format on
      {
        MS_DEBUG_TAG(dtls, "running DTLS transport in local role 'server'");

        this->dtlsTransport->Run(RTC::DtlsTransport::Role::SERVER);
      }

      break;
    }

    case RTC::DtlsTransport::Role::NONE:
    {
      MS_ABORT("local DTLS role not set");
    }
  }
}
```

#### 2.4、this->dtlsTransport->Run——dtls握手、建立connect

以客户端为例，进入this->dtlsTransport->Run()

```cpp
// Set state and notify the listener.
this->state = DtlsState::CONNECTING;
this->listener->OnDtlsTransportConnecting(this);
```

先将Dtls状态设置为CONNECTING，然后把dtlsTransport对象设置给侦听者（WebRtcTransport）

```cpp
case Role::CLIENT:
{
	MS_DEBUG_TAG(dtls, "running [role:client]");
	SSL_set_connect_state(this->ssl);
	SSL_do_handshake(this->ssl);
	SendPendingOutgoingDtlsData();
	SetTimeout();
	break;
}
```

当用户发送连接请求，dtlsTransport的角色为客户端时，dtls就会主动发起连接请求调用`SSL_set_connect_state`这个API，将客户端当作dtls的服务端，对方收到这个连接请求时，就开始握手，调用`SSL_do_handshake`这个API主动握手，接着调用SendPendingOutgoingDtlsData()发送dtls的一些数据

```cpp
case Role::SERVER:
{
	MS_DEBUG_TAG(dtls, "running [role:server]");
	SSL_set_accept_state(this->ssl);
	SSL_do_handshake(this->ssl);
	break;
}
```

若dtlsTransport的角色为服务端时，就会把SSL设置为阻塞模式，然后等待握手

通过以上便建立起了连接

#### 2.5、返回结果

建立连接的结果会赋给`json data = json::object();`

然后通过`request->Accept(data);`反馈给应用层

## 三、创建Producer

```cpp
SetNewProducerIdFromInternal(request->internal, producerId);
```

进入SetNewProducerIdFromInternal这个函数

### 1、SetNewProducerIdFromInternal——拿到producer的ID

```cpp
void Transport::SetNewProducerIdFromInternal(json& internal, std::string& producerId) const
{
	MS_TRACE();
	
  auto jsonProducerIdIt = internal.find("producerId");
	
  if (jsonProducerIdIt == internal.end() || !jsonProducerIdIt->is_string())
		MS_THROW_ERROR("missing internal.producerId");
	
  producerId.assign(jsonProducerIdIt->get<std::string>());
	
  if (this->mapProducers.find(producerId) != this->mapProducers.end())
		MS_THROW_ERROR("a Producer with same producerId already exists");
}
```

搜索producerId，拿到ID后返回，进入构造函数RTC::Producer

### 2、RTC::Producer——Producer的构造函数

在这个构造函数中，主要也是对json数据data进行解析，它包括

  * kind：audio和video
  * rtpparameters：mid、codecs、headerExtensions、encodings、rtcp
  * 等等

```cpp
Producer::Producer(const std::string& id, RTC::Producer::Listener* listener, json& data)
    : id(id), listener(listener)
{
  MS_TRACE();

  auto jsonKindIt = data.find("kind");

  if (jsonKindIt == data.end() || !jsonKindIt->is_string())
    MS_THROW_TYPE_ERROR("missing kind");

  // This may throw.
  this->kind = RTC::Media::GetKind(jsonKindIt->get<std::string>());

  if (this->kind == RTC::Media::Kind::ALL)
    MS_THROW_TYPE_ERROR("invalid empty kind");

  auto jsonRtpParametersIt = data.find("rtpParameters");

  if (jsonRtpParametersIt == data.end() || !jsonRtpParametersIt->is_object())
    MS_THROW_TYPE_ERROR("missing rtpParameters");

  // This may throw.
  this->rtpParameters = RTC::RtpParameters(*jsonRtpParametersIt);

  // Evaluate type.
  this->type = RTC::RtpParameters::GetType(this->rtpParameters);

  // Reserve a slot in rtpStreamByEncodingIdx and rtpStreamsScores vectors
  // for each RTP stream.
  this->rtpStreamByEncodingIdx.resize(this->rtpParameters.encodings.size(), nullptr);
  this->rtpStreamScores.resize(this->rtpParameters.encodings.size(), 0u);

  auto& encoding   = this->rtpParameters.encodings[0];
  auto* mediaCodec = this->rtpParameters.GetCodecForEncoding(encoding);

  if (!RTC::Codecs::Tools::IsValidTypeForCodec(this->type, mediaCodec->mimeType))
  {
    MS_THROW_TYPE_ERROR(
      "%s codec not supported for %s",
      mediaCodec->mimeType.ToString().c_str(),
      RTC::RtpParameters::GetTypeString(this->type).c_str());
  }

  auto jsonRtpMappingIt = data.find("rtpMapping");

  if (jsonRtpMappingIt == data.end() || !jsonRtpMappingIt->is_object())
    MS_THROW_TYPE_ERROR("missing rtpMapping");

  auto jsonCodecsIt = jsonRtpMappingIt->find("codecs");

  if (jsonCodecsIt == jsonRtpMappingIt->end() || !jsonCodecsIt->is_array())
    MS_THROW_TYPE_ERROR("missing rtpMapping.codecs");

  for (auto& codec : *jsonCodecsIt)
  {
    if (!codec.is_object())
      MS_THROW_TYPE_ERROR("wrong entry in rtpMapping.codecs (not an object)");

    auto jsonPayloadTypeIt = codec.find("payloadType");

    // clang-format off
    if (
      jsonPayloadTypeIt == codec.end() ||
      !Utils::Json::IsPositiveInteger(*jsonPayloadTypeIt)
    )
    // clang-format on
    {
      MS_THROW_TYPE_ERROR("wrong entry in rtpMapping.codecs (missing payloadType)");
    }

    auto jsonMappedPayloadTypeIt = codec.find("mappedPayloadType");

    // clang-format off
    if (
      jsonMappedPayloadTypeIt == codec.end() ||
      !Utils::Json::IsPositiveInteger(*jsonMappedPayloadTypeIt)
    )
    // clang-format on
    {
      MS_THROW_TYPE_ERROR("wrong entry in rtpMapping.codecs (missing mappedPayloadType)");
    }

    this->rtpMapping.codecs[jsonPayloadTypeIt->get<uint8_t>()] =
      jsonMappedPayloadTypeIt->get<uint8_t>();
  }

  auto jsonEncodingsIt = jsonRtpMappingIt->find("encodings");

  if (jsonEncodingsIt == jsonRtpMappingIt->end() || !jsonEncodingsIt->is_array())
  {
    MS_THROW_TYPE_ERROR("missing rtpMapping.encodings");
  }

  this->rtpMapping.encodings.reserve(jsonEncodingsIt->size());

  for (auto& encoding : *jsonEncodingsIt)
  {
    if (!encoding.is_object())
      MS_THROW_TYPE_ERROR("wrong entry in rtpMapping.encodings");

    this->rtpMapping.encodings.emplace_back();

    auto& encodingMapping = this->rtpMapping.encodings.back();

    // ssrc is optional.
    auto jsonSsrcIt = encoding.find("ssrc");

    // clang-format off
    if (
      jsonSsrcIt != encoding.end() &&
      Utils::Json::IsPositiveInteger(*jsonSsrcIt)
    )
    // clang-format on
    {
      encodingMapping.ssrc = jsonSsrcIt->get<uint32_t>();
    }

    // rid is optional.
    auto jsonRidIt = encoding.find("rid");

    if (jsonRidIt != encoding.end() && jsonRidIt->is_string())
      encodingMapping.rid = jsonRidIt->get<std::string>();

    // However ssrc or rid must be present (if more than 1 encoding).
    // clang-format off
    if (
      jsonEncodingsIt->size() > 1 &&
      jsonSsrcIt == encoding.end() &&
      jsonRidIt == encoding.end()
    )
    // clang-format on
    {
      MS_THROW_TYPE_ERROR("wrong entry in rtpMapping.encodings (missing ssrc or rid)");
    }

    // If there is no mid and a single encoding, ssrc or rid must be present.
    // clang-format off
    if (
      this->rtpParameters.mid.empty() &&
      jsonEncodingsIt->size() == 1 &&
      jsonSsrcIt == encoding.end() &&
      jsonRidIt == encoding.end()
    )
    // clang-format on
    {
      MS_THROW_TYPE_ERROR(
        "wrong entry in rtpMapping.encodings (missing ssrc or rid, or rtpParameters.mid)");
    }

    // mappedSsrc is mandatory.
    auto jsonMappedSsrcIt = encoding.find("mappedSsrc");

    // clang-format off
    if (
      jsonMappedSsrcIt == encoding.end() ||
      !Utils::Json::IsPositiveInteger(*jsonMappedSsrcIt)
    )
    // clang-format on
    {
      MS_THROW_TYPE_ERROR("wrong entry in rtpMapping.encodings (missing mappedSsrc)");
    }

    encodingMapping.mappedSsrc = jsonMappedSsrcIt->get<uint32_t>();
  }

  auto jsonPausedIt = data.find("paused");

  if (jsonPausedIt != data.end() && jsonPausedIt->is_boolean())
    this->paused = jsonPausedIt->get<bool>();

  // The number of encodings in rtpParameters must match the number of encodings
  // in rtpMapping.
  if (this->rtpParameters.encodings.size() != this->rtpMapping.encodings.size())
  {
    MS_THROW_TYPE_ERROR("rtpParameters.encodings size does not match rtpMapping.encodings size");
  }

  // Fill RTP header extension ids.
  // This may throw.
  for (auto& exten : this->rtpParameters.headerExtensions)
  {
    if (exten.id == 0u)
      MS_THROW_TYPE_ERROR("RTP extension id cannot be 0");

    if (this->rtpHeaderExtensionIds.mid == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::MID)
    {
      this->rtpHeaderExtensionIds.mid = exten.id;
    }

    if (this->rtpHeaderExtensionIds.rid == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::RTP_STREAM_ID)
    {
      this->rtpHeaderExtensionIds.rid = exten.id;
    }

    if (this->rtpHeaderExtensionIds.rrid == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::REPAIRED_RTP_STREAM_ID)
    {
      this->rtpHeaderExtensionIds.rrid = exten.id;
    }

    if (this->rtpHeaderExtensionIds.absSendTime == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::ABS_SEND_TIME)
    {
      this->rtpHeaderExtensionIds.absSendTime = exten.id;
    }

    if (this->rtpHeaderExtensionIds.transportWideCc01 == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::TRANSPORT_WIDE_CC_01)
    {
      this->rtpHeaderExtensionIds.transportWideCc01 = exten.id;
    }

    // NOTE: Remove this once framemarking draft becomes RFC.
    if (this->rtpHeaderExtensionIds.frameMarking07 == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::FRAME_MARKING_07)
    {
      this->rtpHeaderExtensionIds.frameMarking07 = exten.id;
    }

    if (this->rtpHeaderExtensionIds.frameMarking == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::FRAME_MARKING)
    {
      this->rtpHeaderExtensionIds.frameMarking = exten.id;
    }

    if (this->rtpHeaderExtensionIds.ssrcAudioLevel == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::SSRC_AUDIO_LEVEL)
    {
      this->rtpHeaderExtensionIds.ssrcAudioLevel = exten.id;
    }

    if (this->rtpHeaderExtensionIds.videoOrientation == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::VIDEO_ORIENTATION)
    {
      this->rtpHeaderExtensionIds.videoOrientation = exten.id;
    }

    if (this->rtpHeaderExtensionIds.toffset == 0u && exten.type == RTC::RtpHeaderExtensionUri::Type::TOFFSET)
    {
      this->rtpHeaderExtensionIds.toffset = exten.id;
    }
  }
}
```

### 3、Listener——使创建的Producer加入Router的侦听者列表

当RTC::Producer构造完成，返回Transport.cpp执行`cppthis->rtpListener.AddProducer(producer);`

这会把producer加入rtpListener，接着继续执行`cppthis->listener->OnTransportNewProducer(this, producer);`

这个listener是Router的侦听者，返回`Router::OnTransportNewProducer`

### 4、Router::OnTransportNewProducer——把producer加入Transport maps中

```cpp
inline void Router::OnTransportNewProducer(RTC::Transport* /*transport*/, RTC::Producer* producer)
{
	MS_TRACE();
	MS_ASSERT(
	  this->mapProducerConsumers.find(producer) == this->mapProducerConsumers.end(),
	  "Producer already present in mapProducerConsumers");

	if (this->mapProducers.find(producer->id) != this->mapProducers.end())
	{
		MS_THROW_ERROR("Producer already present in mapProducers [producerId:%s]", producer->id.c_str());
	}

	// Insert the Producer in the maps.
	this->mapProducers[producer->id] = producer;
	this->mapProducerConsumers[producer];
	this->mapProducerRtpObservers[producer];
}
```

创建好producer之后，当有数据传来时，便可以根据ssrc找到它对应的producer，然后由producer查看哪些consumer订阅了它，接着就转发数据流了

## 四、创建Consumer

在Transport.cpp里进入下面的case

```cpp
case Channel::Request::MethodId::TRANSPORT_CONSUME
```

在这个case里，会获取到producerId `auto jsonProducerIdIt =request->internal.find("producerId");`

然后还会获取到consumerId，不过它是调用的一个函数 `SetNewConsumerIdFromInternal(request->internal, consumerId);`

接着就开始创建consumer，由于它是多态的，所以会进入一个switch case，它有4种类型：

  * SIMPLE：简单的consumer
  * SIMULCAST：
  * SVC
  * PIPE

```cpp
switch (type)
{
	case RTC::RtpParameters::Type::NONE:
	{
		MS_THROW_TYPE_ERROR("invalid type 'none'");
		break;
	}
	case RTC::RtpParameters::Type::SIMPLE:
	{
		// This may throw.
		consumer = new RTC::SimpleConsumer(consumerId, producerId, this, request->data);
		break;
	}
	case RTC::RtpParameters::Type::SIMULCAST:
	{
		// This may throw.
		consumer = new RTC::SimulcastConsumer(consumerId, producerId, this, request->data);
		break;
	}
	case RTC::RtpParameters::Type::SVC:
	{
		// This may throw.
		consumer = new RTC::SvcConsumer(consumerId, producerId, this, request->data);
		break;
	}
	case RTC::RtpParameters::Type::PIPE:
	{
		// This may throw.
		consumer = new RTC::PipeConsumer(consumerId, producerId, this, request->data);
		break;
	}
}
```

### 1、RTC::SimpleConsumer——对data进行数据解析

以SIMPLE为例，进入RTC::SimpleConsumer

```cpp
SimpleConsumer::SimpleConsumer(
  const std::string& id, const std::string& producerId, RTC::Consumer::Listener* listener, json& data)
  : RTC::Consumer::Consumer(id, producerId, listener, data, RTC::RtpParameters::Type::SIMPLE)
{
	MS_TRACE();
	// Ensure there is a single encoding.
	if (this->consumableRtpEncodings.size() != 1u)
		MS_THROW_TYPE_ERROR("invalid consumableRtpEncodings with size != 1");
	auto& encoding         = this->rtpParameters.encodings[0];
	const auto* mediaCodec = this->rtpParameters.GetCodecForEncoding(encoding);
	this->keyFrameSupported = RTC::Codecs::Tools::CanBeKeyFrame(mediaCodec->mimeType);
	// Create RtpStreamSend instance for sending a single stream to the remote.
	CreateRtpStream();
}
```

这段代码主要也是对data数据的解析，然后在代码的末尾段构造了一个Rtp数据流，进入CreateRtpStream()

### 2、CreateRtpStream()——根据data数据确定consumer内部细节

_Consumer的本质就是一个Rtp数据流_

```cpp
void SimpleConsumer::CreateRtpStream()
{
  MS_TRACE();

  auto& encoding         = this->rtpParameters.encodings[0];
  const auto* mediaCodec = this->rtpParameters.GetCodecForEncoding(encoding);

  MS_DEBUG_TAG(
    rtp, "[ssrc:%" PRIu32 ", payloadType:%" PRIu8 "]", encoding.ssrc, mediaCodec->payloadType);

  // Set stream params.
  RTC::RtpStream::Params params;

  params.ssrc        = encoding.ssrc;
  params.payloadType = mediaCodec->payloadType;
  params.mimeType    = mediaCodec->mimeType;
  params.clockRate   = mediaCodec->clockRate;
  params.cname       = this->rtpParameters.rtcp.cname;

  // Check in band FEC in codec parameters.
  if (mediaCodec->parameters.HasInteger("useinbandfec") && mediaCodec->parameters.GetInteger("useinbandfec") == 1)
  {
    MS_DEBUG_TAG(rtp, "in band FEC enabled");

    params.useInBandFec = true;
  }

  // Check DTX in codec parameters.
  if (mediaCodec->parameters.HasInteger("usedtx") && mediaCodec->parameters.GetInteger("usedtx") == 1)
  {
    MS_DEBUG_TAG(rtp, "DTX enabled");

    params.useDtx = true;
  }

  // Check DTX in the encoding.
  if (encoding.dtx)
  {
    MS_DEBUG_TAG(rtp, "DTX enabled");

    params.useDtx = true;
  }

  for (const auto& fb : mediaCodec->rtcpFeedback)
  {
    if (!params.useNack && fb.type == "nack" && fb.parameter.empty())
    {
      MS_DEBUG_2TAGS(rtp, rtcp, "NACK supported");

      params.useNack = true;
    }
    else if (!params.usePli && fb.type == "nack" && fb.parameter == "pli")
    {
      MS_DEBUG_2TAGS(rtp, rtcp, "PLI supported");

      params.usePli = true;
    }
    else if (!params.useFir && fb.type == "ccm" && fb.parameter == "fir")
    {
      MS_DEBUG_2TAGS(rtp, rtcp, "FIR supported");

      params.useFir = true;
    }
  }

  // Create a RtpStreamSend for sending a single media stream.
  size_t bufferSize = params.useNack ? 600u : 0u;

  this->rtpStream = new RTC::RtpStreamSend(this, params, bufferSize);
  this->rtpStreams.push_back(this->rtpStream);

  // If the Consumer is paused, tell the RtpStreamSend.
  if (IsPaused() || IsProducerPaused())
    this->rtpStream->Pause();

  const auto* rtxCodec = this->rtpParameters.GetRtxCodecForEncoding(encoding);

  if (rtxCodec && encoding.hasRtx)
    this->rtpStream->SetRtx(rtxCodec->payloadType, encoding.rtx.ssrc);
}
```

通过创建params获得了5个参数，分别是

  * ssrc
  * payloadType
  * mimeType
  * clockRate
  * cname

以及后面通过if判断来确定是否使用FEC、DTX，以及Feedback丢包重传机制是使用NACK、PLI、FIR的哪一种

接着创建了一个RTC::RtpStreamSend对象，传入的三个参数分别是

  * this——这个RtpStreamSend对象
  * params——之前获得了5个参数
  * bufferSize——缓存数组

创建好了这个对象后，就把它压入rtpStreams中保存起来

### 3、consumer小结

当共享者的数据源源不断地传过来，mediasoup就会根据它的ssrc找到对应的生产者，通过生产者再找到对应的消费者，接着再通过RtpStreamSend发送给用户

<hr>

 
#### <p>原文出处：<a href='https://blog.csdn.net/Frederick_Fung/article/details/107387579' target='blank'>Mediasoup源码分析（四）流的转发</a></p>

_传输媒体流的通道的建立在Media soup源码分析（三）中已经说明，实际上流的转发是依赖于Socket_

## 创建socket

### WebRtcTransport

下述socket的创建函数在C++的WebRtcTransport类的构造函数中

```cpp
auto* udpSocket = new RTC::UdpSocket(this, listenIp.ip);
```

这行代码创建了UdpSocket，且有多少个listenIp就创建多少个socket

### UdpSocket

进入UdpSocket的构造函数，它调用了父类**::UdpSocket**的构造函数，实际上在参数中，还调用了**PortManager::BindUdp(ip)**，它通过udp获得了端口，并且生成了一个与libuv绑定的handle

```cpp
UdpSocket::UdpSocket(Listener* listener, std::string& ip)
  : // This may throw.
    ::UdpSocket::UdpSocket(PortManager::BindUdp(ip)), listener(listener)
{
  MS_TRACE();
}
```

### ::UdpSocket

在父类的构造函数中，启动了一个**uvHandle**，并且申请了**onRecv**这个API

```cpp
UdpSocket::UdpSocket(uv_udp_t* uvHandle) : uvHandle(uvHandle)
{
  MS_TRACE();
  int err;
  this->uvHandle->data = static_cast<void*>(this);

  err = uv_udp_recv_start(
    this->uvHandle, static_cast<uv_alloc_cb>(onAlloc), static_cast<uv_udp_recv_cb>(onRecv));
  if (err != 0)
  {
    uv_close(reinterpret_cast<uv_handle_t*>(this->uvHandle), static_cast<uv_close_cb>(onClose));
    MS_THROW_ERROR("uv_udp_recv_start() failed: %s", uv_strerror(err));
  }

  // Set local address.
  if (!SetLocalAddress())
  {
    uv_close(reinterpret_cast<uv_handle_t*>(this->uvHandle), static_cast<uv_close_cb>(onClose));
    MS_THROW_ERROR("error setting local IP and port");
  }
}
```

## 传递数据包

### onRecv

onRecv是一个全局静态函数，为了贯彻面向对象的思想，这里继续把参数传给socket->OnUvRecv，

```cpp
inline static void onRecv(
  uv_udp_t* handle, ssize_t nread, const uv_buf_t* buf, const struct sockaddr* addr, unsigned int flags)
{
  auto* socket = static_cast<UdpSocket*>(handle->data);
  if (socket)
    socket->OnUvRecv(nread, buf, addr, flags);
}
```

### OnUvRecv

在这个函数体内，重要的是下面这行代码

```cpp
// Notify the subclass.
UserOnUdpDatagramReceived(reinterpret_cast<uint8_t*>(buf->base), nread, addr);
```

它在子类（RTC\UdpSocket）里实现了这个函数

### UserOnUdpDatagramReceived

在这个函数体内，又转手给OnUdpSocketPacketReceived的侦听者

```cpp
void UdpSocket::UserOnUdpDatagramReceived(const uint8_t* data, size_t len, const struct sockaddr* addr)
{
  MS_TRACE();
  if (this->listener == nullptr)
  {
    MS_ERROR("no listener set");
    return;
  }
  // Notify the reader.
  this->listener->OnUdpSocketPacketReceived(this, data, len, addr);
}
```

### OnUdpSocketPacketReceived

在这个函数体内，创建了一个tuple，然后又进入OnPacketReceived这个函数

```cpp
inline void WebRtcTransport::OnUdpSocketPacketReceived(
  RTC::UdpSocket* socket, const uint8_t* data, size_t len, const struct sockaddr* remoteAddr)
{
  MS_TRACE();
  RTC::TransportTuple tuple(socket, remoteAddr);
  OnPacketReceived(&tuple, data, len);
}
```

## 对数据包处理

### OnPacketReceived

在这个函数中，对收到的数据进行区分，然后分别对STUN、RTCP、RTP、DTLS做处理

```cpp
inline void WebRtcTransport::OnPacketReceived(
  RTC::TransportTuple* tuple, const uint8_t* data, size_t len)
{
  MS_TRACE();
  // Increase receive transmission.
  RTC::Transport::DataReceived(len);
  // Check if it's STUN.
  if (RTC::StunPacket::IsStun(data, len))
  {
    OnStunDataReceived(tuple, data, len);
  }
  // Check if it's RTCP.
  else if (RTC::RTCP::Packet::IsRtcp(data, len))
  {
    OnRtcpDataReceived(tuple, data, len);
  }
  // Check if it's RTP.
  else if (RTC::RtpPacket::IsRtp(data, len))
  {
    OnRtpDataReceived(tuple, data, len);
  }
  // Check if it's DTLS.
  else if (RTC::DtlsTransport::IsDtls(data, len))
  {
    OnDtlsDataReceived(tuple, data, len);
  }
  else
  {
    MS_WARN_DEV("ignoring received packet of unknown type");
  }
}
```

### STUN

#### OnStunDataReceived

先用Parse对数据进行分析，这个函数是对协议头和协议体按位分析，STUN的规范标准请参考RFC5389

然后再交给iceServer的ProcessStunPacket方法来处理

```cpp
inline void WebRtcTransport::OnStunDataReceived(
  RTC::TransportTuple* tuple, const uint8_t* data, size_t len)
{
  MS_TRACE();
  RTC::StunPacket* packet = RTC::StunPacket::Parse(data, len);
  if (!packet)
  {
    MS_WARN_DEV("ignoring wrong STUN packet received");
    return;
  }
  // Pass it to the IceServer.
  this->iceServer->ProcessStunPacket(packet, tuple);
  delete packet;
}
```

#### ProcessStunPacket

在这个函数中，首先对STUN的method进行判断，**若不是Binding请求就出错**，若是Binding请求则继续

```cpp
if (packet->GetMethod() != RTC::StunPacket::Method::BINDING)
{
  if (packet->GetClass() == RTC::StunPacket::Class::REQUEST)
  {
    MS_WARN_TAG(
      ice,
      "unknown method %#.3x in STUN Request => 400",
      static_cast<unsigned int>(packet->GetMethod()));
    // Reply 400.
    RTC::StunPacket* response = packet->CreateErrorResponse(400);
    response->Serialize(StunSerializeBuffer);
    this->listener->OnIceServerSendStunPacket(this, response, tuple);
    delete response;
  }
  else
  {
    MS_WARN_TAG(
      ice,
      "ignoring STUN Indication or Response with unknown method %#.3x",
      static_cast<unsigned int>(packet->GetMethod()));
  }
  return;
}
```

**接着是对证书指纹的判断**

```cpp
// Must use FINGERPRINT (optional for ICE STUN indications).
if (!packet->HasFingerprint() && packet->GetClass() != RTC::StunPacket::Class::INDICATION)
{
  if (packet->GetClass() == RTC::StunPacket::Class::REQUEST)
  {
    MS_WARN_TAG(ice, "STUN Binding Request without FINGERPRINT => 400");
    // Reply 400.
    RTC::StunPacket* response = packet->CreateErrorResponse(400);
    response->Serialize(StunSerializeBuffer);
    this->listener->OnIceServerSendStunPacket(this, response, tuple);
    delete response;
  }
  else
  {
    MS_WARN_TAG(ice, "ignoring STUN Binding Response without FINGERPRINT");
  }
  return;
}
```

**然后是对字段的检查**

```cpp
if (!packet->HasMessageIntegrity() || (packet->GetPriority() == 0u) || packet->GetUsername().empty())
{
  MS_WARN_TAG(ice, "mising required attributes in STUN Binding Request => 400");
  // Reply 400.
  RTC::StunPacket* response = packet->CreateErrorResponse(400);
  response->Serialize(StunSerializeBuffer);
  this->listener->OnIceServerSendStunPacket(this, response, tuple);
  delete response;
  return;
}
```

**进行授权检查**

通过CheckAuthentication对**接收到的**u_frag和pwd与**本地的**u_frag和pwd进行比较，若一致则返回OK

```cpp
switch (packet->CheckAuthentication(this->usernameFragment, this->password))
{
  case RTC::StunPacket::Authentication::OK:
  {
    if (!this->oldPassword.empty())
    {
      MS_DEBUG_TAG(ice, "new ICE credentials applied");
      this->oldUsernameFragment.clear();
      this->oldPassword.clear();
    }
    break;
  }
  case RTC::StunPacket::Authentication::UNAUTHORIZED:
  {
    // We may have changed our usernameFragment and password, so check
    // the old ones.
    // clang-format off
    if (
      !this->oldUsernameFragment.empty() &&
      !this->oldPassword.empty() &&
      packet->CheckAuthentication(this->oldUsernameFragment, this->oldPassword) == RTC::StunPacket::Authentication::OK
    )
    // clang-format on
    {
      MS_DEBUG_TAG(ice, "using old ICE credentials");
      break;
    }
    MS_WARN_TAG(ice, "wrong authentication in STUN Binding Request => 401");
    // Reply 401.
    RTC::StunPacket* response = packet->CreateErrorResponse(401);
    response->Serialize(StunSerializeBuffer);
    this->listener->OnIceServerSendStunPacket(this, response, tuple);
    delete response;
    return;
  }
  case RTC::StunPacket::Authentication::BAD_REQUEST:
  {
    MS_WARN_TAG(ice, "cannot check authentication in STUN Binding Request => 400");
    // Reply 400.
    RTC::StunPacket* response = packet->CreateErrorResponse(400);
    response->Serialize(StunSerializeBuffer);
    this->listener->OnIceServerSendStunPacket(this, response, tuple);
    delete response;
    return;
  }
}
```

### DTLS

#### OnDtlsDataReceived——DTLS状态判断

在这块函数中，会对DTLS的状态进行分析，有两种，分别是connecting和connected，前者表示新加入的用户，后者表示断线重连，进入Process DtlsData

```cpp
inline void WebRtcTransport::OnDtlsDataReceived(
  const RTC::TransportTuple* tuple, const uint8_t* data, size_t len)
{
  MS_TRACE();
  // Ensure it comes from a valid tuple.
  if (!this->iceServer->IsValidTuple(tuple))
  {
    MS_WARN_TAG(dtls, "ignoring DTLS data coming from an invalid tuple");
    return;
  }
  // Trick for clients performing aggressive ICE regardless we are ICE-Lite.
  this->iceServer->ForceSelectedTuple(tuple);
  // Check that DTLS status is 'connecting' or 'connected'.
  if (
    this->dtlsTransport->GetState() == RTC::DtlsTransport::DtlsState::CONNECTING ||
    this->dtlsTransport->GetState() == RTC::DtlsTransport::DtlsState::CONNECTED)
  {
    MS_DEBUG_DEV("DTLS data received, passing it to the DTLS transport");
    this->dtlsTransport->ProcessDtlsData(data, len);
  }
  else
  {
    MS_WARN_TAG(dtls, "Transport is not 'connecting' or 'connected', ignoring received DTLS data");
    return;
  }
}
```

#### ProcessDtlsData

在这个函数中，CheckStatus这个方法是检查SSL的状态

```cpp
// Check SSL status and return if it is bad/closed.
if (!CheckStatus(read))
  return;
```

而真正的握手是在DtlsTransport::Run函数里的SSL_do_handshake(this->ssl)这个方法

### RTP

### RTCP

未完待续…
