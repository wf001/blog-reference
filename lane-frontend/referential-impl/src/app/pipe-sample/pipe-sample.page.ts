import { Component, OnInit } from '@angular/core';
import { NUM } from '@const'

@Component({
    selector: 'app-pipe-sample',
    templateUrl: './pipe-sample.page.html',
    styleUrls: ['./pipe-sample.page.scss'],
})
export class PipeSamplePage implements OnInit {
    unixTime:string = "1645933718"

    constructor() {
        console.log(NUM)
    }

    ngOnInit() {
    }

}
