/*
 * delete.ts
 *
 * Created by Ruibin.Chow on 2025/02/16.
 * Copyright (c) 2025年 Ruibin.Chow All rights reserved.
 */

import fs from 'fs';
import path  from 'path';


let removeList = [
  path.join(process.cwd(), '../dist')
];

removeList.forEach(value => {
  console.log('remove: ', value);
  if (fs.existsSync(value)) {
    fs.rmSync(value, { recursive: true, force: true });
  }
});
