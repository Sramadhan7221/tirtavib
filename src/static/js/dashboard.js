const WARNING = "warning";
const NORMAL = "success";
const ERROR = "danger";
const btn = ``

const areaName = []
$(document).ready(function () {
   let counter = 1;
   const area_id = [1,2,3,4,5];
   area_id.forEach(async (areaId) => await callAPI(areaId))
   console.log(areaName)
   setInterval(()=>{
      $('#area_name').html(areaName[counter-1])
      document.getElementById('radio'+counter).checked = true;
      counter++;

      if(counter>13){
         counter = 1;
      }
   },3000);

   setInterval(() => {
      area_id.forEach((areaId) => callAPI(areaId))
   }, 7200000);

})

async function generateCard(data,area) {
   var result = "";
   let counter = 0,
      batch = 0;
   Object.values(data).forEach(function (o) {
      var nama = o.nama, accel = o.accel, velocity = o.velocity, peak_peak = o.peak_peak, status = o.status, dna12 = o.dna12, dna500 = o.dna500 , updated = new Date(o.last_update);
      var content = `<p class="mb-0"> Velocity : <b>${velocity.toPrecision(3)}</b> mm/s (RMS)</p>
                     <p class="mb-0"> Acceleration : <b>${accel.toPrecision(3)}</b> g (pk)</p>
                     <p class="mb-0"> Peak peak : <b>${peak_peak.toPrecision(3)}</b></p>`;
      if (dna12 > 0 || dna500 > 0) {
         content = `<p class="mb-0"> DNA12 g : <b>${dna12.toPrecision(3)}</b> pk-pk </p>
                     <p class="mb-0"> DNA500 g : <b>${accel.toPrecision(4)}</b> pk-pk </p>`;
      }
      switch (status) {
         case "alert":
            status = WARNING;
            break;
         case "danger":
            status = ERROR;
            break;
         default:
            status = NORMAL;
            break;
      }

      const card = `<div class="col-lg-2 col-6">
                  <div class="small-box ${status} opacity-25">
                     <div class="inner opacity-125">
                        <h5>${nama}</h5>
                        ${content}
                     </div>
                     <span  class="small-box-footer">Update: ${updated.toLocaleDateString('en-GB')} ${updated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>
                  </div>
               </div>`;
      result += card;
      counter++;

      if (counter == 15) {
         counter -= counter;
         $(`#${area+batch}`).append(result);
         result = ""
         batch++;
      }
   })
}

async function callAPI(areaId) {
   $.get("/dashboard/v1?area="+areaId,async function (o) {
      var area_name = o.data.area_name,
         jml_mp = o.data.jumlah,
         batch = Math.floor(jml_mp/15),
         remains = jml_mp % 15,
         data = o.data.measure_points;

      for (let index = 0; index < batch; index++) {
         if (remains == 0 && index == batch)
            break;
            
         const content = `<div class="slide">
                  <div class="content">
                     
                     <div class="m-4">
                        <div class="row" id="${area_name+index}">
                        </div> 
                     </div>
                  </div>
            </div>`;   
         
         $("#container").append(content);
         areaName.push(area_name) 
      }

      $(".slide").first().addClass("first")
      await generateCard(data,area_name);
   });
}