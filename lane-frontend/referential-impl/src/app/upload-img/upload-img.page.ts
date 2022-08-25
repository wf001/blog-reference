import { Component } from '@angular/core';
import axios from 'axios'
import { Platform, ModalController, ActionSheetController } from '@ionic/angular';
import { DomSanitizer } from '@angular/platform-browser';

import { Camera, CameraOptions } from '@ionic-native/camera/ngx';
import imageToBase64 from 'image-to-base64/browser'
import { Diagnostic } from '@ionic-native/diagnostic/ngx';
import { env } from '@const';

declare const Buffer;

@Component({
    selector: 'app-upload-img',
    templateUrl: './upload-img.page.html',
    styleUrls: ['./upload-img.page.scss'],
})
export class UploadImgPage {
    ax: any;
    base64Image: any;
    imgForPreview: any;
    isDesktop: boolean = false;

    constructor(
        private camera: Camera,
        public ASC: ActionSheetController,
        private DS: DomSanitizer,
        private platform: Platform
    ) {
        this.ax = axios.create()
        if (this.platform.platforms().includes('desktop')) {
            this.isDesktop = true;
        }
    }


    async submit() {
        try {
            //Get S3 Pre-signed url for uploading object.
            let res: any = await this.ax.post(env.BACKEND_ENDPOINT, {}, {})
            const decodedFile = new Buffer(this.base64Image, 'base64')
            let opt = {
                headers: {
                    'Content-Type': 'image/jpeg',
                    'Content-Encoding': 'base64',
                }
            };
            res = await this.ax.put(res.data.url, decodedFile, opt)
            alert(res.status)
        } catch (e) {
            alert(e)
        }
    }

    async pickImage(sourceType) {
        const options: CameraOptions = {
            quality: 100,
            sourceType: sourceType,
            destinationType: this.camera.DestinationType.DATA_URL,
            encodingType: this.camera.EncodingType.JPEG,
            mediaType: this.camera.MediaType.PICTURE
        };

        try {
            // For browser
            if (this.isDesktop) {
                let file_uri = env.IMG_PATH_FOR_BROWSER
                await imageToBase64(file_uri).then(res => {
                    this.base64Image = res
                    this.imgForPreview = this.DS.bypassSecurityTrustUrl(
                        'data:image/jpeg;charset=utf-8;base64,' + this.base64Image
                    );
                })
                // For Android 
            } else {
                this.camera.getPicture(options).then((data) => {
                    this.base64Image = data
                    this.imgForPreview = this.DS.bypassSecurityTrustUrl(
                        'data:image/jpeg;charset=utf-8;base64,' + this.base64Image
                    );
                }).catch(error => alert(error))
            }
        } catch (e) { alert(e) }
    }
    async handlePicker() {
        const lib = this.camera.PictureSourceType.PHOTOLIBRARY;
        const camera = this.camera.PictureSourceType.CAMERA;

        const actionSheet = await this.ASC.create({
            header: 'Select Image source',
            buttons: [
                {
                    text: 'Load from Library',
                    handler: () => {
                        this.pickImage(lib);
                    }
                },
                {
                    text: 'Use Camera',
                    handler: () => {
                        this.pickImage(camera);
                    }
                },
                {
                    text: 'Cancel',
                    role: 'cancel'
                }
            ]
        });
        await actionSheet.present();
    }

}
