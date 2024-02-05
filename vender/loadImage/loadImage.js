/*
 * loadImage.js
 *
 * Created by Ruibin.Chow on 2023/06/08.
 * Copyright (c) 2023年 Ruibin.Chow All rights reserved.
 */

var imageCount = 0;
var currentImage = 0; //存储图片加载到的位置，避免每次都从第一张图片开始遍历

function loadingImage() {
  imageCount = document.getElementsByTagName('img').length;
  lazyload(); //页面载入完毕加载可是区域内的图片
  window.onscroll = lazyload;
}

function lazyload() { //监听页面滚动事件
  var seeHeight = document.documentElement.clientHeight; //可见区域高度
  var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;; //滚动条距离顶部高度
  var img = document.getElementsByTagName("img");

  for (var i = currentImage; i < imageCount; i++) {
    if (img[i].offsetTop < seeHeight + scrollTop) {
      if (img[i].getAttribute("src").indexOf("img_loading.gif") != -1) {
        let dataSrc = img[i].getAttribute("data-src");
        
        if (dataSrc.substr(0, 4) == "http") {
          dataSrc = dataSrc.replace(/^(http)[s]*(\:\/\/)/,'https://images.weserv.nl/?url=');
          
          img[i].setAttribute("referrer", "no-referrer|origin|unsafe-url");
          // <meta name="referrer" content="no-referrer" />
        }

        img[i].src = dataSrc;
      }
      currentImage = i + 1;
    }
  }
}
