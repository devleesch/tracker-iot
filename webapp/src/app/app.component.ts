import { Component, OnDestroy, OnInit } from '@angular/core';
import { Observable, Subscription, timer } from 'rxjs';
import { ConfigService } from './services/config.service';
import { PositionService } from './services/position.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  config: any;
  last_nmea: any;

  constructor(private configService: ConfigService, private positionService: PositionService) {}

  ngOnInit() {
    this.showConfig();
    this.showLastNmea();
  }

  showConfig() {
    this.configService
        .get()
        .subscribe((response: any) => {
          this.config = response;
        });
  }

  showLastNmea() {
    this.positionService
        .getLastNmea()
        .subscribe((response: any) => {
          this.last_nmea = response;
        });
  }

}
