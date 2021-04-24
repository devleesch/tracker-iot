import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class PositionService {

  private baseUrl = "api/position";

  constructor(private http: HttpClient) { }

  last() {
    return this.http.get(this.baseUrl + '/last');
  }
}
