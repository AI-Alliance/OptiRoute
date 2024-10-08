import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Vehicle } from '../models/Vehicle';
import { PlaceMarker } from '../models/PlaceMarker';
import { v4 as uuidv4 } from 'uuid';
import { Observable, map, switchMap, tap } from 'rxjs';
import { Solution } from '../models/Solution';
import { GMapsService } from './g-maps.service';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  constructor(private httpClient: HttpClient, private gMapsService: GMapsService) { 
    
  }

  getAlgorithms(){
    return this.httpClient.get<{algorithms: string[]}>(environment.backendAddress + '/algorithms').pipe(map(response => response.algorithms));
  }

  getSolution(placeMarkers: PlaceMarker[], vehicles: Vehicle[], algorithm: string, algorithmParams: string): Observable<Solution>{
    return this.gMapsService.getMatrix(placeMarkers).pipe(
      switchMap((matrix) => {
        let taskId = uuidv4();
        return this.sendTask(taskId, vehicles, placeMarkers, algorithm, algorithmParams, matrix).pipe(
          switchMap( () => {
            return this.pollSolution(taskId);
          })
        )
      }),
      tap((solution: Solution) =>  {
        solution.algorithm = algorithm;
        solution.activeV = solution.vehicles.filter(v => v.route.places.length > 2).length;
        solution.stats = {
          max: solution.vehicles.reduce((max, vehicle) => vehicle.route.duration_sum > max ? vehicle.route.duration_sum : max, 0),
          sum: solution.vehicles.reduce((sum, vehicle) => sum + vehicle.route.duration_sum, 0)
        }
      })
    )
  }

  private pollSolution(taskId: string){


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

  private sendTask(taskId:string, vehicles: Vehicle[], places: PlaceMarker[], algorithm: string, algorithmParams: string, matrix: number[][]){
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
      algorithm_params: algorithmParams,
      rows: matrixToSend
    });
  }
}
