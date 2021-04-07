import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ProcessService {

  constructor(private http: HttpClient) { }

  status() {
    return this.http.get('api/process_status');
  }

  stop(process: string) {
    return this.http.post('api/stop', "process="+process);
  }

}
