import { Pipe, PipeTransform } from '@angular/core';
import * as dayjs from 'dayjs'
import * as relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/en'

@Pipe({
  name: 'customPipe'
})
export class CustomPipe implements PipeTransform {

  transform(value: number, ...args: unknown[]): unknown {
      dayjs.extend(relativeTime);
      dayjs.locale('en');
      return dayjs(value*1000).fromNow();
  }

}
