export class MapRoute{

    totalDurationSeconds: number = 0;

    constructor(public directions: google.maps.DirectionsResult, 
        public options: google.maps.DirectionsRendererOptions){
        
        for (const leg of this.directions.routes[0].legs) {
            this.totalDurationSeconds+= leg.duration?.value ?? 0;
        }
    }
}