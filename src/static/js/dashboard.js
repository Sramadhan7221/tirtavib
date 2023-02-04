const WARNING = "bg-warning";
const NORMAL = "bg-success";
const ERROR = "bg-danger";
const btn = ``
$(document).ready(function () {
   let counter = 1;
   const area_id = [1,2,3,4,5];
   area_id.forEach(async (areaId) => await callAPI(areaId))
   setInterval(()=>{
      document.getElementById('radio'+counter).checked = true;
      counter++;

      if(counter>18){
         counter = 1;
      }
   },10000);

   setInterval(() => {
      area_id.forEach((areaId) => callAPI(areaId))
   }, 7200000);

})

async function generateCard(data,area) {
   var result = "";
   let counter = 0,
      batch = 0;
   Object.values(data).forEach(function (o) {
      var nama = o.nama, accel = o.accel, velocity = o.velocity, peak_peak = o.peak_peak, status = o.status, updated = new Date(o.last_update);
      
      switch (status) {
         case "warning":
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
                  <div class="small-box ${status}">
                     <div class="inner">
                     <h5>${nama}</h5>
                     <p class="mb-0">Velocity : <b>${Math.ceil(velocity)}</b> mm/s (RMS)</p>
                     <p class="mb-0"> Acceleration : <b>${Math.ceil(accel)}</b> g (pk)</p>
                     <p> Peak peak : <b>${Math.ceil(peak_peak)}</b></p>
                     </div>
                     <span  class="small-box-footer">Last update: ${updated.toLocaleDateString('en-GB')} ${updated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>
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

      for (let index = 0; index <= batch; index++) {
         if (remains == 0 && index == batch)
            break;
            
         const content = `<div class="slide">
                  <div class="content">
                     <!-- Navbar -->
                     <nav class=" navbar-expand navbar-white navbar-light layout-navbar-fixed ">
                     <!-- Left navbar links -->

                     <!-- Right navbar links -->
                     <ul class="navbar-nav">
                        <li class="nav-item align-items-center ">
                              <!-- Brand Logo -->
                              <a href="" class="navbar-brand ml-4">
                                 <img src="{{ url_for('static', filename="img/AGC.jpg")}}" alt="AGC" class="brand-image rounded" style="opacity: .8"width="90" height="100%">
                              </a>
                        </li>
                        <li class="nav-item mx-auto mt-2 align-items-center">
                              <h2 class="bg-primary px-1 shadow rounded ">${area_name}</h2>
                        </li>
                        <li class="navbar-nav pr-3 align-items-center">
                              <h5>Vibration Monitoring</h5>
                        </li>
                        <li class="nav-item align-items-center">
                              <a class="nav-link mt-2" data-widget="fullscreen" href="#" role="button">
                              <i class="fas fa-expand-arrows-alt"></i>
                              </a>
                        </li>
                     </ul>
                     </nav>
                     <!-- /.navbar -->
                     <div class="m-4">
                        <div class="row" id="${area_name+index}">
                        </div> 
                     </div>
                  </div>
            </div>`;   
         
         $("#container").append(content);
      }

      $(".slide").first().addClass("first")
      await generateCard(data,area_name);
   });
}