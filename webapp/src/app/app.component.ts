import { Component, OnInit } from '@angular/core';
import { ConfigService } from './services/config.service';
import { PositionService } from './services/position.service';
import { ProcessService } from './services/process.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  config: any;
  lastNmea: any;
  gpsState: boolean;
  senderState: boolean;

  constructor(
    private configService: ConfigService
    , private positionService: PositionService
    , private processService: ProcessService) {}

  ngOnInit() {
    this.loadConfig();
    this.loadLastNmea();
    this.loadProcess();
  }

  loadConfig() {
    this.configService
        .get()
        .subscribe((response: any) => {
          this.config = response;
        });
  }

  loadLastNmea() {
    this.positionService
        .last()
        .subscribe((response: any) => {
          this.lastNmea = response;
        });
  }

  loadProcess() {
    this.processService
        .status()
        .subscribe((response: any) => this.updateStates(response));
  }

  onGpsChange() {
    this.gpsState ? this.startProcess('gps') : this.stopProcess('gps');
  }

  onSenderChange() {
    this.senderState ? this.startProcess('sender') : this.stopProcess('sender');
  }

  private startProcess(process: string) {
    this.processService
        .start(process)
        .subscribe((response: any) => this.updateStates(response));
  }

  private stopProcess(process: string) {
    this.processService
        .stop(process)
        .subscribe((response: any) => this.updateStates(response));
  }

  private updateStates(response: any) {
    this.gpsState = response.gps;
    this.senderState = response.sender;
  }

}
