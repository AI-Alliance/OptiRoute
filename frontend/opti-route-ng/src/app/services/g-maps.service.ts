import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MapDirectionsService, MapGeocoder, MapGeocoderResponse } from '@angular/google-maps';
import { Observable, catchError, forkJoin, map, of } from 'rxjs';
import { environment } from 'src/environments/environment';
import { PlaceMarker } from '../models/PlaceMarker';

@Injectable({
  providedIn: 'root'
})
export class GMapsService {
  apiLoaded: Observable<boolean>;
  private distanceMatrixService: google.maps.DistanceMatrixService | undefined;

  
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
    
  }

  getGeoInfo(latLng: google.maps.LatLng){
    return this.geocoder.geocode({
      location: latLng
    })
  }

  getGeoInfoById(placeId: string){
    return this.geocoder.geocode({
      placeId: placeId
    })
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

  getDistMatrix(placeMarkers: PlaceMarker[]): Observable<number[][]>{    

    return this.getOneRequestMatrix(placeMarkers, placeMarkers);
    // let observers: Observable<number[][]>[] = []


    // return forkJoin(observers).pipe( );
  
  }

  private getOneRequestMatrix(origins: PlaceMarker[], destinations: PlaceMarker[]): Observable<number[][]>{
    return (new Observable<DistanceMatrixResponse>((observer) => {
      console.log('origins', origins);
      console.log('destinations', destinations);
      this.distanceMatrixService?.getDistanceMatrix(
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
    })).pipe(this.googleMatrixToDistanceMatrixMapper());
  }

  private googleMatrixToDistanceMatrixMapper(){
    return map( (distanceMatrixResponse: DistanceMatrixResponse) => {
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

interface DistanceMatrixResponse{
  response: google.maps.DistanceMatrixResponse | null,
  status: google.maps.DistanceMatrixStatus
}