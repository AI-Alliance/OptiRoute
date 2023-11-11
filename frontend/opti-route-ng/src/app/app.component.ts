import { Component, OnInit, ViewChild } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of } from 'rxjs';
import { MapInfoWindow, MapMarker, MapGeocoder, MapDirectionsService } from '@angular/google-maps';
import { PlaceMarker, PlaceType } from './models/PlaceMarker';
import { Vehicle } from './models/Vehicle';
import { TaskService } from './services/task.service';
import { GMapsService } from './services/g-maps.service';




@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  PlaceType: typeof PlaceType = PlaceType;
  selectedType: PlaceType = PlaceType.DEPOT;

  
  options: google.maps.MapOptions = {
    center: {lat: 54.36975172380843, lng: 18.610832380277717},
    zoom: 20,
    
  };

  @ViewChild(MapInfoWindow) infoWindow: MapInfoWindow | undefined;

  lastMarker: PlaceMarker | undefined;


  placeMarkers: PlaceMarker[] = [];
  vehicles: Vehicle[] = [];


  constructor(private geocoder: MapGeocoder, private taskService: TaskService, protected gMapsService: GMapsService){
    
  }


  directionsResults$!: Observable<google.maps.DirectionsResult | undefined>;
  loadRoute(){
    
    this.directionsResults$ = this.gMapsService.loadRoute(this.placeMarkers[0], this.placeMarkers[1]);
  }

  ngOnInit(): void {
   
  
  }

  getGeoInfo(marker: PlaceMarker){
    this.gMapsService.getGeoInfo(marker).subscribe((r) => console.log(r))
  }

  addMarker(event: google.maps.MapMouseEvent) {
    if(!event.latLng){
      return;
    }
    
    if(this.hasDepotMarker() && this.selectedType == PlaceType.DEPOT){
      return;
    }
    let m = new PlaceMarker(event.latLng, this.selectedType);
     

    this.placeMarkers.push(m);
    if(this.selectedType == PlaceType.DEPOT){
      this.selectedType = PlaceType.CLIENT;
    }
  }

  hasDepotMarker(){
    return this.placeMarkers.find((m) => m.type == PlaceType.DEPOT);
  }

  deleteMarker(marker: PlaceMarker){
    let markerToDelete = this.placeMarkers.findIndex(m => m.uuid == marker.uuid);
    if (markerToDelete < 0){
      return;
    }
    
    this.placeMarkers.splice(markerToDelete, 1);
  }
  

  openInfoWindow(marker: PlaceMarker, mapMarker: MapMarker) {
    this.lastMarker = marker;
    this.infoWindow?.open(mapMarker);
  }

  addVehicle(){
    this.vehicles.push(new Vehicle(0));
  }

  sendTask(){
    this.gMapsService.getDistMatrix(this.placeMarkers).subscribe((response: google.maps.DistanceMatrixResponse | null) => {
      if(!response){
        return;
      }

      this.taskService.sendTask(this.vehicles, this.placeMarkers, response).subscribe((response)=> console.log(response));
    })
    
  }
}
