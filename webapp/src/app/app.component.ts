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

  public static readonly GPS_PROCESS: string = "GPS";
  public static readonly SENDER_PROCESS: string = "SENDER";
  public static readonly TRACK_MODE_PROCESS: string = 'TRACK_MODE';

  config: any;
  lastNmea: any;
  processStates: any;

  constructor(
    private configService: ConfigService
    , private positionService: PositionService
    , private processService: ProcessService) {}

  ngOnInit() {
    this.loadConfig();
    this.loadLastNmea();
    this.statuses();
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

  statuses() {
    this.processService
        .status()
        .subscribe((response: any) => this.updateStates(response));
  }

  onGpsChange() {
    this.processStates.gps ? this.startProcess(AppComponent.GPS_PROCESS) : this.stopProcess(AppComponent.GPS_PROCESS);
  }

  onSenderChange() {
    this.processStates.sender ? this.startProcess(AppComponent.SENDER_PROCESS) : this.stopProcess(AppComponent.SENDER_PROCESS);
  }

  onTrackModeChange() {
    this.updateConfig(this.config);
  }

  powerOff() {
    
  }

  reboot() {

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
    this.processStates = response;
  }

  private updateConfig(config: any) {
    this.configService
        .update(config)
        .subscribe((response: any) => this.config = response);
  }

}
