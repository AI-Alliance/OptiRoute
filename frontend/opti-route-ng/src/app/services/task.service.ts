import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Vehicle } from '../models/Vehicle';
import { PlaceMarker } from '../models/PlaceMarker';
import { v4 as uuidv4 } from 'uuid';
import { Observable, map } from 'rxjs';
import { Solution } from '../models/Solution';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  constructor(private httpClient: HttpClient) { 
    
  }

  getAlgorithms(){
    return this.httpClient.get<{algorithms: string[]}>(environment.backendAddress + '/algorithms').pipe(map(response => response.algorithms));
  }

  getSolution(taskId: string){


    return new Observable<Solution>((observer) => {
      const handler = setInterval(() => 
        this.httpClient.get<Solution>(environment.backendAddress + '/solutions/'+taskId).subscribe((response: Solution) => {
          clearInterval(handler);
          observer.next(response);
          observer.complete();
        }), 100
      )
    })
  }

  sendTask(taskId:string, vehicles: Vehicle[], places: PlaceMarker[], algorithm: string, matrix: number[][]){
    let placesToSend = [];

    for(let i = 0; i < places.length; i++){
      let place = places[i];
      placesToSend.push({place_id: place.placeId, place_index: i, demand: place.demand});
    }

    let vehiclesToSend = vehicles.map((v)=> {return {vehicle_id: v.uuid, capacity: v.capacity}});
    
    let matrixToSend: {elements: number[]}[] = matrix.map(row => {return {elements: row}} );

    return this.httpClient.post(environment.backendAddress +'/tasks',{
      task_id: taskId,
      places: placesToSend,
      vehicles: vehiclesToSend,
      algorithm_type: algorithm,
      rows: matrixToSend
    });
  }
}
