import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MapDirectionsService, MapGeocoder, MapGeocoderResponse } from '@angular/google-maps';
import { Observable, catchError, forkJoin, map, of } from 'rxjs';
import { environment } from 'src/environments/environment';
import { PlaceMarker } from '../models/PlaceMarker';
import { DistanceMatrix } from '../models/DistanceMatrix';

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

  onApiLoaded(){
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

  getDistMatrix(placeMarkers: PlaceMarker[]): Observable<DistanceMatrix>{    

    if(placeMarkers.length <= 10){
      return this.getOneRequestMatrix(placeMarkers, placeMarkers);
    }

    
    return this.getCompositionMatrix(placeMarkers);
  }

  getOneRequestMatrix(origins: PlaceMarker[], destinations: PlaceMarker[]): Observable<DistanceMatrix>{
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

  googleMatrixToDistanceMatrixMapper(){
    return map( (distanceMatrixResponse: DistanceMatrixResponse) => {
      if(!distanceMatrixResponse.response){
        throw new Error(distanceMatrixResponse.status);
      }
      let googleMatrix: google.maps.DistanceMatrixResponse = distanceMatrixResponse.response;
      let matrix: DistanceMatrix = { rows: []};
      for (const row of googleMatrix.rows){
        matrix.rows.push({elements: row.elements.map(e => e.duration.value)});
      }
      return matrix;
    })
  }

  getCompositionMatrix(placeMarkers: PlaceMarker[]): Observable<DistanceMatrix>{
    let observers: Observable<DistanceMatrix>[] = []

    placeMarkers.forEach( p => {
      observers.push(this.getOneRequestMatrix([p], placeMarkers));
    })

    return forkJoin(observers).pipe( map(responses => {
      let matrix: DistanceMatrix = { rows: []};
      for (const m of responses) {
        matrix.rows.push(m.rows[0]);
      }

      return matrix;
    }))
  }



}

interface DistanceMatrixResponse{
  response: google.maps.DistanceMatrixResponse | null,
  status: google.maps.DistanceMatrixStatus
}