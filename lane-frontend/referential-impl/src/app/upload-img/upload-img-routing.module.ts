import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { UploadImgPage } from './upload-img.page';

const routes: Routes = [
  {
    path: '',
    component: UploadImgPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class UploadImgPageRoutingModule {}
