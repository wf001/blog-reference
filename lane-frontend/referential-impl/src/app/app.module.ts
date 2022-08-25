import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouteReuseStrategy } from '@angular/router';

import { IonicModule, IonicRouteStrategy } from '@ionic/angular';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { PipeModule } from './custom-pipe/pipe.module';
import { Camera } from '@ionic-native/camera/ngx';
import { Diagnostic } from '@ionic-native/diagnostic/ngx';

@NgModule({
  declarations: [
      AppComponent,
  ],
  entryComponents: [],
  imports: [
      BrowserModule,
      // pipe
      PipeModule,
      IonicModule.forRoot(),
      AppRoutingModule
  ],
  providers: [
      Camera,
      Diagnostic,
      { provide: RouteReuseStrategy, useClass: IonicRouteStrategy }
  ],
  bootstrap: [
      AppComponent
  ],
})
export class AppModule {}
