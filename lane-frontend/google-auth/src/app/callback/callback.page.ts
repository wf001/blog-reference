import { Component, OnInit } from '@angular/core';
import { HomePage } from '../home/home.page'
import axios from 'axios'
import { Storage } from '@ionic/storage-angular'

@Component({
    selector: 'app-callback',
    templateUrl: './callback.page.html',
    styleUrls: ['./callback.page.scss'],
})
export class CallbackPage implements OnInit {
    st: any;

    constructor(
        private storage: Storage,
    ) {
        this.init().then(async() =>
            await this.setIdTokenForBrowser()
        )
    }
    ngOnInit(){}

    async init() {
        this.st = await this.storage.create();
    }
    async setIdTokenForBrowser() {
        let url = window.location.href.split('#')
        let params = url[1].split('&')
        let code = ''
        let token = ''
        params.forEach(p => {
            if (p.includes('code')) {
                code = p.split('=')[1]
            }
            else if (p.includes('id_token')) {
                token = p.split('=')[1]
            }
        })

        await this.st.set('id_token', token)
        window.location.href = "/home"

    }
}
