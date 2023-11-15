import { Component, OnInit, ViewChild } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, forkJoin, map, of, tap } from 'rxjs';
import { MapInfoWindow, MapMarker, MapGeocoder, MapDirectionsService, MapGeocoderResponse } from '@angular/google-maps';
import { PlaceMarker, PlaceType } from './models/PlaceMarker';
import { Vehicle } from './models/Vehicle';
import { TaskService } from './services/task.service';
import { GMapsService } from './services/g-maps.service';
import { v4 as uuidv4 } from 'uuid';
import { Solution } from './models/Solution';




@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  PlaceType: typeof PlaceType = PlaceType;
  selectedType: PlaceType = PlaceType.DEPOT;
  taskLoading: boolean = false;
  
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


  directionsResults: Array<google.maps.DirectionsResult | undefined> = [];
  directionsOrder = [];
  directionsRendererOptions: google.maps.DirectionsRendererOptions[] = []; 
  loadRoute(placesId:string[], color: string){
    
    let placesLatLng: google.maps.LatLng[] = [];
    let observers: Observable<MapGeocoderResponse>[] = []
    for (const placeId of placesId) {

      observers.push(
        this.gMapsService.getGeoInfoById(placeId)
      )
    }
    forkJoin(observers).subscribe((responses) => {
      responses.forEach((r) => {
        placesLatLng.push(r.results[0].geometry.location);
      })  
      this.gMapsService.loadRoute(placesLatLng).subscribe(r => {
        this.directionsResults.push(r);
        this.directionsRendererOptions.push({markerOptions:{visible: false}, polylineOptions: {strokeColor: color, strokeOpacity: 0.5, strokeWeight: 5}});
      })
      
    })
  }

  clearRoutes(){
    this.directionsRendererOptions = [];
    this.directionsResults = [];
  }

  refreshMarkersText(){
    this.placeMarkers.forEach(m => m.setText(null));
  }

  showSolution(solution: Solution){
    let colors = ['red', 'green', 'purple'];

    this.clearRoutes();
    this.refreshMarkersText();
    for (const vehicle of solution.vehicles) {
      for(let i = 0; i < vehicle.route.length; i++){
        this.placeMarkers.find((m) => (m.placeId == vehicle.route[i].place_id) && (m.type == PlaceType.CLIENT))?.setText(i.toString());
      }

      this.loadRoute(vehicle.route.map((p)=> p.place_id), colors.pop() ?? 'black');
    }
  }

  ngOnInit(): void {
    
  
  }

 

  getGeoInfo(marker: PlaceMarker){
    this.gMapsService.getGeoInfo(marker.latLng).subscribe((r) => console.log(r))
  }

  addMarker(event: google.maps.MapMouseEvent) {
    if(!event.latLng){
      return;
    }
    
    if(this.hasDepotMarker() && this.selectedType == PlaceType.DEPOT){
      return;
    }
    let m = new PlaceMarker(event.latLng, this.selectedType);
     
    this.gMapsService.getGeoInfo(m.latLng).subscribe((r) => {
      m.placeId = r.results[0].place_id;
      m.latLng = r.results[0].geometry.location;
      m.description = r.results[0].formatted_address;
    }
    
    )
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
  removeVehicle(id: string){
    let i = this.vehicles.findIndex(v => v.uuid == id);
    if (i > -1) {
      this.vehicles.splice(i, 1);
    }
  }

  taskDataIsReady(){
    return this.vehicles.length && (this.placeMarkers.length > 1) && this.hasDepotMarker()
  }

  sendTask(){
    this.gMapsService.getDistMatrix(this.placeMarkers).subscribe((matrix: google.maps.DistanceMatrixResponse | null) => {
      if(!matrix){
        return;
      }
      let taskId = uuidv4();
      this.taskLoading = true;
      this.taskService.sendTask(taskId, this.vehicles, this.placeMarkers, matrix).subscribe(()=> {
        this.taskService.getSolution(taskId).subscribe((solution) => {
          this.taskLoading = false;
          this.showSolution(solution)
        })
      });
    })
    
  }
}
