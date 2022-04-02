import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SystemService {

  private _baseUrl = "api/system";

  constructor(private http: HttpClient) { }

  poweroff() {
    return this.http.get(this._baseUrl + '/poweroff');
  }

  reboot() {
    return this.http.get(this._baseUrl + '/reboot');
  }
}
