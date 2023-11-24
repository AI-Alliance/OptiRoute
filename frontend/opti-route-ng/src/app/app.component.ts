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
import { FileService } from './services/file.service';
import { MapRoute } from './models/MapRoute';



@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  PlaceType: typeof PlaceType = PlaceType;
  selectedType: PlaceType = PlaceType.DEPOT;

  algorithms: string[] = [];

  selectedAlgorithm: string = '';

  taskLoading: boolean = false;
  
  options: google.maps.MapOptions = {
    center: {lat: 54.36975172380843, lng: 18.610832380277717},
    zoom: 20,
    
  };

  @ViewChild(MapInfoWindow) infoWindow: MapInfoWindow | undefined;

  lastMarker: PlaceMarker | undefined;


  placeMarkers: PlaceMarker[] = [];
  vehicles: Vehicle[] = [];


  constructor(private geocoder: MapGeocoder, private taskService: TaskService, protected gMapsService: GMapsService, private fileService: FileService){
    
  }

  routes: MapRoute[]=[];
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
        if(!r){
          console.error('Undefined route');
          return;
        }
        this.routes.push(new MapRoute(r,{markerOptions:{visible: false}, polylineOptions: {strokeColor: color, strokeOpacity: 0.5, strokeWeight: 5}}));
        this.updateSolutionsStats();
      })
      
    })
  }

  clearRoutes(){
    this.routes = []
    this.placeMarkers.forEach(m => m.setText(null));
  }

  showSolution(solution: Solution){
    let colors = ['red', 'green', 'purple'];

    this.clearRoutes();
    for (const vehicle of solution.vehicles) {
      for(let i = 0; i < vehicle.route.places.length; i++){
        this.placeMarkers.find((m) => (m.placeId == vehicle.route.places[i].place_id) && (m.type == PlaceType.CLIENT))?.setText(i.toString());
      }

      this.loadRoute(vehicle.route.places.map((p)=> p.place_id), colors.pop() ?? 'black');
    }

  }

  solutionsStats: {max: number, avg: number} = {max: 0, avg: 0};
  updateSolutionsStats(){
    let durations = this.routes.map((r)=> r.totalDurationSeconds);
    this.solutionsStats= {
      max: Math.max(...durations),
      avg: durations.reduce((a, b) => a + b, 0) / durations.length
    };
  }

  ngOnInit(): void {
    this.taskService.getAlgorithms().subscribe((algorithms) => this.algorithms = algorithms);
  }

  

  getGeoInfo(marker: PlaceMarker){
    this.gMapsService.getGeoInfo(marker.latLng).subscribe((r) => console.log(r))
  }

  onMarkerAdd(event: google.maps.MapMouseEvent) {
    if(!event.latLng){
      return;
    }
    
    if(this.hasDepotMarker() && this.selectedType == PlaceType.DEPOT){
      return;
    }
    this.addMarker(event.latLng, this.selectedType);

    if(this.selectedType == PlaceType.DEPOT){
      this.selectedType = PlaceType.CLIENT;
    }
  }

  addMarker(latLng: google.maps.LatLng, type: PlaceType){
    let m = new PlaceMarker(latLng, type);
     
    this.gMapsService.getGeoInfo(m.latLng).subscribe((r) => {
      m.placeId = r.results[0].place_id;
      m.latLng = r.results[0].geometry.location;
      m.description = r.results[0].formatted_address;
    })

    if(type == PlaceType.DEPOT){
      this.placeMarkers.unshift(m);
    } else {
      this.placeMarkers.push(m);
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
    return this.vehicles.length && (this.placeMarkers.length > 1) && this.hasDepotMarker() && this.selectedAlgorithm.length;
  }

  getSolution(){
    this.taskLoading = true;

    this.taskService.getSolution(this.placeMarkers, this.vehicles, this.selectedAlgorithm).subscribe(solution => {
      this.showSolution(solution);
      this.taskLoading = false;
    })    
  }

  onFileSelect(event: any){
    const file: File = event.target.files[0];
    if(file){
      this.fileService.readFileData(file).subscribe(data => {
        this.placeMarkers = data.places;
        this.vehicles = data.vehicles;
      })
    }
  }

  downloadInput(){
    this.fileService.downloadInput(this.placeMarkers, this.vehicles);
  }
}

