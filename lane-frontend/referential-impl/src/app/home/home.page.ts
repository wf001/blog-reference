import { Component } from '@angular/core';
import { NavController } from '@ionic/angular';

@Component({
    selector: 'app-home',
    templateUrl: 'home.page.html',
    styleUrls: ['home.page.scss'],
})
export class HomePage {

    constructor(
        private nav: NavController
    ) { }
    onTapPipe() {
        this.nav.navigateForward('/pipe-sample');
    }
    onTapUploadImg() {
        this.nav.navigateForward('/upload-img');
    }

}
