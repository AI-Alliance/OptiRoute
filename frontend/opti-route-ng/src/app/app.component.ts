import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
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
import { GoogleMap } from '@angular/google-maps';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {

  @ViewChild('myMap')
  map!: GoogleMap;

  PlaceType: typeof PlaceType = PlaceType;
  selectedType: PlaceType = PlaceType.DEPOT;

  generatorMode: boolean = false;
  generatorLoading: boolean = false;
  generator = {
    min: 0,
    max: 0,
    radius: 1000,
    places: 50
  }


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


  apiLoaded: boolean = false;
  constructor(private geocoder: MapGeocoder, private taskService: TaskService, protected gMapsService: GMapsService, private fileService: FileService){
   
    this.gMapsService.apiLoaded.subscribe((loaded) => {
      this.apiLoaded = loaded;
      setTimeout(() => {
        
        google.maps.importLibrary("places").then(() => {
          if(this.map.googleMap){
            this.gMapsService.placesService = new google.maps.places.PlacesService(this.map.googleMap);

          }

        });
          

        

      }, 1000)
      
    }
    )
    
  }

  ngOnInit(): void {
    
    
    this.taskService.getAlgorithms().subscribe((algorithms) => this.algorithms = algorithms);
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

  getTotalDemand(){
    return this.placeMarkers.reduce((a, v) => a + v.demand, 0);
  }
  getTotalCapacity(){
    return this.vehicles.reduce((a, v) => a + v.capacity, 0);
  }

  getGeoInfo(marker: PlaceMarker){
    this.gMapsService.getGeoInfo(marker.latLng).subscribe((r) => console.log(r))
  }

  onMapClick(event: google.maps.MapMouseEvent) {
    if(!event.latLng){
      return;
    }

    if(this.generatorMode){
      this.generatorMode = false;
      this.generatorLoading = true;
      this.gMapsService.getNerbyPlaces(event.latLng, this.generator.radius).subscribe(places => {
        places = places.splice(0, this.generator.places);
        places.forEach(p => {
          if(!p.geometry?.location){
            return;
          }

          let pM = new PlaceMarker(p.geometry?.location, PlaceType.CLIENT);
          pM.demand = Math.floor(Math.random() * (this.generator.max - this.generator.min) + this.generator.min);
          pM.placeId = p.place_id ?? '';
          pM.description = p.vicinity ?? '';
          this.placeMarkers.push(pM);
        })
        this.generatorLoading = false;
      })
      
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
    this.vehicles.push(new Vehicle(this.vehicles[this.vehicles.length-1]?.capacity ?? 0));
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

  lastSolution?: Solution;
  getSolution(){
    this.taskLoading = true;

    this.taskService.getSolution(this.placeMarkers, this.vehicles, this.selectedAlgorithm).subscribe(solution => {
      this.showSolution(solution);
      this.lastSolution = solution;
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
  downloadResult(){
    if(!this.lastSolution){
      return;
    }
    this.fileService.downloadResult(this.lastSolution);
  }
}

