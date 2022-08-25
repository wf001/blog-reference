import { NgModule } from '@angular/core'
import { CommonModule } from '@angular/common'
import { CustomPipe } from './custom-pipe.pipe'


@NgModule({
    imports: [
        CommonModule
    ],
    declarations: [
        CustomPipe
    ],
    exports: [
        CustomPipe
    ]
})
export class PipeModule {}
