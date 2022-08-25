import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouteReuseStrategy } from '@angular/router';

import { IonicModule, IonicRouteStrategy } from '@ionic/angular';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { GooglePlus } from '@ionic-native/google-plus/ngx';
import { File } from '@ionic-native/file/ngx';
import { HTTP } from '@ionic-native/http/ngx'
import { IonicStorageModule } from '@ionic/storage-angular'
import { OAuthModule } from 'angular-oauth2-oidc';
import { HttpClientModule } from '@angular/common/http';
import { HomePage } from './home/home.page'

@NgModule({
    declarations: [AppComponent],
    entryComponents: [],
    imports: [
        BrowserModule, IonicModule.forRoot(),
        IonicStorageModule.forRoot(),
        OAuthModule.forRoot(),
        HttpClientModule,
        AppRoutingModule
    ],
    providers: [
        GooglePlus,
        File,
        HTTP,
        HomePage,
        { provide: RouteReuseStrategy, useClass: IonicRouteStrategy }
    ],
    bootstrap: [AppComponent],
})
export class AppModule { }
