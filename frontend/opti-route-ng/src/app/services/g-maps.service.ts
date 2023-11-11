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
    this.apiLoaded = this.httpClient.jsonp('https://maps.googleapis.com/maps/api/js?key=' + environment.gMapsApiKey, 'callback').pipe(
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

   getGeoInfo(marker: PlaceMarker){
    return this.geocoder.geocode({
      location: marker.latLng
    })
  }

  
  loadRoute(origin: PlaceMarker, destination: PlaceMarker){
    const request: google.maps.DirectionsRequest = {
      destination: destination.latLng,
      origin: origin.latLng,
      travelMode: google.maps.TravelMode.DRIVING
    };
    return this.mapDirectionsService.route(request).pipe(map(response => response.result));
  }

  getDistMatrix(placeMarkers: PlaceMarker[]){

    // for (const placeMarker of placeMarkers) {
    //   this.getGeoInfo(placeMarker).subscribe((r) => placeMarker.placeId = r.results[0].place_id)
    // }

   
    return new Observable<google.maps.DistanceMatrixResponse | null>((observer) => {
      this.distanceMatrixService?.getDistanceMatrix(
        {
          origins: placeMarkers.map(m => m.latLng),
          destinations: placeMarkers.map(m => m.latLng),
          travelMode: google.maps.TravelMode.DRIVING
        },
        (response: google.maps.DistanceMatrixResponse | null) => {
          observer.next(response);
          observer.complete()
        }
      )
    })


  }

}
