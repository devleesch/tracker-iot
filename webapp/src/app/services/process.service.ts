import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ProcessService {

  private _baseUrl = "api/process";

  constructor(private http: HttpClient) { }

  status() {
    return this.http.get(this._baseUrl + '/status');
  }

  start(process: string) {
    return this.http.post(this._baseUrl + '/start', {"process": process});
  }

  stop(process: string) {
    return this.http.post(this._baseUrl + '/stop', {"process": process});
  }

}
