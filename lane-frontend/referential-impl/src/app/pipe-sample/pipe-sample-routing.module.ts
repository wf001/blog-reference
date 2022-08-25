import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { PipeSamplePage } from './pipe-sample.page';

const routes: Routes = [
  {
    path: '',
    component: PipeSamplePage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PipeSamplePageRoutingModule {}
