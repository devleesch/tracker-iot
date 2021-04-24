import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {

  private _baseUrl = "api/config";

  constructor(private http: HttpClient) { }

  get() {
    return this.http.get(this._baseUrl);
  }
  
}
