import { Component } from '@angular/core';
import { File } from '@ionic-native/file/ngx';
import { GooglePlus } from '@ionic-native/google-plus/ngx';
import { HTTP } from '@ionic-native/http/ngx'
import { Storage } from '@ionic/storage-angular'
import { Platform } from '@ionic/angular'
import axios from 'axios'
import { env } from '../environment'

@Component({
    selector: 'app-home',
    templateUrl: 'home.page.html',
    styleUrls: ['home.page.scss'],
})
export class HomePage {

    userData: any = {};
    st: any;
    host: string = ''
    ax: any;
    isDesktop: boolean = false

    constructor(
        private googlePlus: GooglePlus,
        private http: HTTP,
        private storage: Storage,
        private platform: Platform,
    ) {
        this.init()
    }

    async init() {
        this.st = await this.storage.create();
        this.ax = axios.create()

        if (this.platform.platforms().includes('desktop')) {
            this.isDesktop = true
        }
    }


    async signUp() {
        if (this.isDesktop) {
            this.browserSignUp();
        } else {
            this.nativeSignUp();
        }
    }

    private nativeSignUp() {
        this.googlePlus.login({
            webClientId: env.GOOGLE_WEB_CLIENT_ID,
            offline: true
        }).then(async (result) => {
            await this.st.set('id_token', result.idToken)
        }).catch(err => this.userData = `Error ${JSON.stringify(err)}`);
    }

    private browserSignUp() {
        let uri = "https://accounts.google.com/o/oauth2/auth"
        let client_id = env.GOOGLE_WEB_CLIENT_ID
        let redirect = 'http://localhost:8081/callback'
        let scope = "https://www.googleapis.com/auth/userinfo.email"
        let target = uri + "?response_type=code id_token&access_type=offline&client_id=" + client_id + "&redirect_uri=" + redirect + "&scope=" + scope
        location.href = target

    }

    async signOut() {
        if (!this.isDesktop) {
            await this.googlePlus.logout()
                .then(result => this.userData = result)
                .catch(err => this.userData = `Error ${JSON.stringify(err)}`);
        }
        this.st.remove('id_token');
        this.st.remove('refresh_token');
        alert("signed out")
    }

    async get() {
        let id = await this.st.get('id_token')
        alert(id)
    }

}
