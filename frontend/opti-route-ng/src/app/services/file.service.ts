import { Injectable } from '@angular/core';
import { PlaceMarker, PlaceType } from '../models/PlaceMarker';
import { Vehicle } from '../models/Vehicle';
import * as FileSaver from 'file-saver';
import { Observable, forkJoin, map, switchMap } from 'rxjs';
import { GMapsService } from './g-maps.service';
import { MapGeocoderResponse } from '@angular/google-maps';
import * as Papa from 'papaparse';
import { Solution } from '../models/Solution';

@Injectable({
  providedIn: 'root'
})
export class FileService {

  constructor(private gMapsService: GMapsService) { }

  downloadInput(placesToSave: PlaceMarker[], vehiclesToSave: Vehicle[]){
    let places: FilePlace[] = placesToSave.map(({placeId, type, demand}) => ({placeId, type, demand}) );
    let vehicles: FileVehicle[] = vehiclesToSave.map(({capacity})=>({capacity}));

    const blob = new Blob([JSON.stringify({places, vehicles})], { type: 'application/json' });

    FileSaver.saveAs(blob,  "opti-input_"+new Date().toLocaleDateString()+".json");
  }

  readFileData(file: File): Observable<{places: PlaceMarker[], vehicles: Vehicle[]}>{
    return this.readFile(file).pipe(
      switchMap((jsonData) => this.parseJsonObject(jsonData))
    )
  }

  downloadResult(solution:Solution){
    let data = [{
      algorithm: solution.algorithm,
      cN: solution.placesD.length,
      cSum: solution.placesD.reduce((a,v) => a + v),
      cMin: solution.placesD.reduce((a,v) => Math.min(a, v)),
      cMax: solution.placesD.reduce((a,v) => Math.max(a, v)),
      vN: solution.vehiclesC.length,
      vSum: solution.vehiclesC.reduce((a,v) => a + v),
      vMin: solution.vehiclesC.reduce((a,v) => Math.min(a, v)),
      vMax: solution.vehiclesC.reduce((a,v) => Math.max(a, v)),
     
      avg: solution.stats.avg,
      max: solution.stats.max,
      sum: solution.stats.sum
    }];

    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
 
    FileSaver.saveAs(blob,  "opti-result_"+new Date().toLocaleDateString()+".csv");
  }


  private readFile(file: File){
    return new Observable<{places: Array<FilePlace>, vehicles: Array<FileVehicle>}>(observer => {
      const reader = new FileReader();

      reader.onload = (e: any) => {
        const jsonContent = e.target.result;
  
        try {
          const jsonData = JSON.parse(jsonContent);
          console.log(jsonData);
          observer.next(jsonData);
        } catch (error) {
          observer.error('Error parsing JSON');
        }
      };

      reader.readAsText(file);
    });    
  }

  private importMarkers(places: Array<FilePlace>) {
    let observers: Observable<MapGeocoderResponse>[] = []

    places.forEach(p => {
      observers.push(this.gMapsService.getGeoInfoById(p.placeId));
    });

    return forkJoin(observers).pipe( map(responses => {
      let placeMarkers: PlaceMarker[] = [];

      for(let i=0; i < responses.length; i++){
        let result = responses[i].results[0];
        let m = new PlaceMarker(result.geometry.location, places[i].type);
        m.placeId = result.place_id;
        m.demand = places[i].demand;
        m.description = result.formatted_address;
        placeMarkers.push(m);
      }
      return placeMarkers;
    }));
  }

  private parseJsonObject(jsonContent: {places: Array<FilePlace>, vehicles: Array<FileVehicle>}){
    return this.importMarkers(jsonContent.places).pipe( map(places => {
      return {places: places, vehicles: jsonContent.vehicles.map(v => new Vehicle(v.capacity))}
    }) )
  }
}


interface FilePlace{
  placeId: string, 
  type: PlaceType,
  demand: number
}

interface FileVehicle{
  capacity: number
}