/*
 * index.tsx
 *
 * Created by Ruibin.Chow on 2025/02/20.
 * Copyright (c) 2025年 Ruibin.Chow All rights reserved.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '@:/App';
import logger from '@:/log';


const container = document.createElement('div');
container.id = 'root';
document.body.appendChild(container);

logger.info('aaaa');

const root = createRoot(document.getElementById('root')!);
root.render(<App />);