import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MapDirectionsService, MapGeocoder, MapGeocoderResponse } from '@angular/google-maps';
import { Observable, catchError, forkJoin, map, of, tap } from 'rxjs';
import { environment } from 'src/environments/environment';
import { PlaceMarker } from '../models/PlaceMarker';
import * as FileSaver from 'file-saver';

@Injectable({
  providedIn: 'root'
})
export class GMapsService {
  apiLoaded: Observable<boolean>;
  private distanceMatrixService!: google.maps.DistanceMatrixService;
  public placesService!: google.maps.places.PlacesService;
  
  constructor(private httpClient: HttpClient, private  mapDirectionsService: MapDirectionsService, private geocoder: MapGeocoder) {
    
    this.apiLoaded = this.httpClient.jsonp('https://maps.googleapis.com/maps/api/js?key=' + environment.gMapsApiKey + '&language=en', 'callback').pipe(
      map(() => {this.onApiLoaded(); return true}),
      catchError((error) => {
        console.error(error);
        return of(false);
      }),
      
    );
  }


  private onApiLoaded(){
    this.distanceMatrixService = new google.maps.DistanceMatrixService();
    // this.placesService = new google.maps.places.PlacesService(google.maps.Map);
    
  }

  getNerbyPlaces(location: google.maps.LatLng, radius: number): Observable<google.maps.places.PlaceResult[]>{
    let r: google.maps.places.PlaceSearchRequest;
    return new Observable<google.maps.places.PlaceResult[]>(observable => {
      this.placesService.nearbySearch({
        location: location,
        radius: radius,
        type: "cafe"
      }, (result: google.maps.places.PlaceResult[] | null) => {
        if(!result){
          return observable.error('No places');
        }
        observable.next(result);
        observable.complete();
      })
    })
   
  }

  // getNerbyPlacesPage(location: google.maps.LatLng, nextPageToken){

  // }

  getGeoInfo(latLng: google.maps.LatLng){
    
    return this.geocoder.geocode({
      location: latLng
    })
  }

  private geoCache: Map<string, MapGeocoderResponse> = new Map();
  getGeoInfoById(placeId: string){
    const cacheKey = placeId;

    let cachedData = this.geoCache.get(cacheKey);
    if(cachedData){
      return of(cachedData);
    }

    return this.geocoder.geocode({
      placeId: placeId
    }).pipe(tap(geoData => this.geoCache.set(cacheKey, geoData)))
  }

  
  loadRoute(placesLatLng:google.maps.LatLng[]){
    let route = [...placesLatLng];
    let origin = route[0];
    route.splice(0,1);

    let destination = route[route.length-1];
    route.splice(route.length-1,1);

    let waypoints: google.maps.DirectionsWaypoint[] = route.map((p) => {return{
      location: p
    }});
    

    const request: google.maps.DirectionsRequest = {
      destination: destination,
      origin: origin,
      waypoints: waypoints,
      travelMode: google.maps.TravelMode.DRIVING
    };
    return this.mapDirectionsService.route(request).pipe(map(response => response.result));
  }

  private matrixCache: Map<string, number[][]> = new Map();
  getMatrix(placeMarkers: PlaceMarker[]): Observable<number[][]>{    
    const cacheKey = placeMarkers.map(marker => `${marker.placeId}`).join(',');

    let cachedMatrix = this.matrixCache.get(cacheKey);
    if(cachedMatrix){
      return of(cachedMatrix);
    }

    return this.getCompositionMatrix(placeMarkers).pipe(tap( matrix => this.matrixCache.set(cacheKey, matrix)));
  }


  private getCompositionMatrix(placeMarkers: PlaceMarker[]){
    let observables: Observable<number[][]>[] = [];

    const baseMatrixOrder = 10; 
    
    let numberOfMatricesInDemension = Math.ceil(placeMarkers.length / baseMatrixOrder);


    for(let r=0; r<numberOfMatricesInDemension;r++){
      for(let c=0; c<numberOfMatricesInDemension;c++){
        observables.push(this.getOneRequestMatrix(
          placeMarkers.slice(0 + r*baseMatrixOrder, baseMatrixOrder + r*baseMatrixOrder), placeMarkers.slice(0 + c*baseMatrixOrder, baseMatrixOrder + c*baseMatrixOrder)
          ));
        
      }
    }

    return forkJoin(observables).pipe(map(matrices => {
      let matrix: number[][] = Array.from(Array(placeMarkers.length), _ => Array(placeMarkers.length).fill(0));// zeroes
      for(let r=0; r<numberOfMatricesInDemension;r++){
        for(let c=0; c<numberOfMatricesInDemension;c++){
          let matrixToInsert = matrices[r*numberOfMatricesInDemension + c];

          matrix = this.insertMatrix(matrixToInsert, matrix, r*baseMatrixOrder, c*baseMatrixOrder);

        }
      }
      // this.saveMatrix(matrix);
      return matrix;
    }))
  }

  private saveMatrix(matrix: number[][]){


    let output = '';
    for (const row of matrix) {
      for (const col of row) {
        output+=col + ', ';
      }
      output+='\n';
    }
    var blob = new Blob([output], {type: "text/plain;charset=utf-8"});
    FileSaver.saveAs(blob,  "matrix.txt");

  }

  private insertMatrix(matrix: number[][], destination: number[][], row: number, column: number){
    

    let rows = matrix.length;
    let cols = matrix[0].length;

    for(let r=0; r<rows;r++){
      for(let c=0; c<cols;c++){
        destination[row+r][column + c] = matrix[r][c];
      }
    }

    return destination;
  }

  private getOneRequestMatrix(origins: PlaceMarker[], destinations: PlaceMarker[]): Observable<number[][]>{
    return (new Observable<GoogleMatrixResponse>((observer) => {
      this.distanceMatrixService.getDistanceMatrix(
        {
          origins: origins.map(m => m.latLng),
          destinations: destinations.map(m => m.latLng),
          travelMode: google.maps.TravelMode.DRIVING
        },
        (response: google.maps.DistanceMatrixResponse | null, status: google.maps.DistanceMatrixStatus) => {
          
          observer.next({response, status});
          observer.complete()
        },
      )
    })).pipe(this.googleMatrixToDurationMatrixMapper());
  }

  private googleMatrixToDurationMatrixMapper(){
    return map( (distanceMatrixResponse: GoogleMatrixResponse) => {
      if(!distanceMatrixResponse.response){
        throw new Error(distanceMatrixResponse.status);
      }
      let googleMatrix: google.maps.DistanceMatrixResponse = distanceMatrixResponse.response;
      let matrix: number[][] = [];
      for (const row of googleMatrix.rows){
        matrix.push(row.elements.map(e => e.duration.value));
      }
      return matrix;
    })
  }

}

interface GoogleMatrixResponse{
  response: google.maps.DistanceMatrixResponse | null,
  status: google.maps.DistanceMatrixStatus
}