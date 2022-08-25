import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { PipeSamplePageRoutingModule } from './pipe-sample-routing.module';

import { PipeSamplePage } from './pipe-sample.page';
import { PipeModule } from '../custom-pipe/pipe.module'

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    PipeModule,
    PipeSamplePageRoutingModule
  ],
  declarations: [PipeSamplePage]
})
export class PipeSamplePageModule {}
