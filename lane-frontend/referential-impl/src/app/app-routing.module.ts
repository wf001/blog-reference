import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'home',
    loadChildren: () => import('./home/home.module').then( m => m.HomePageModule)
  },
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'pipe-sample',
    loadChildren: () => import('./pipe-sample/pipe-sample.module').then( m => m.PipeSamplePageModule)
  },
  {
    path: 'upload-img',
    loadChildren: () => import('./upload-img/upload-img.module').then( m => m.UploadImgPageModule)
  },
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
