const WARNING = "warning";
const NORMAL = "success";
const ERROR = "danger";
const btn = ``

var areaName = []
let last_slider = 0;
$(document).ready(function () {
   let counter = 1;
   const area_id = [1,2,3,4,5];

   setTimeout(() => {
      area_id.forEach(async (areaId) => {
         await callAPI(areaId)
         $(".ring").addClass("d-none")
      })
   }, 2000);
   
   setInterval(()=>{
      $('#area_name').html(areaName[counter-1])
      document.getElementById('radio'+counter).checked = true;
      counter++;

      if(counter>last_slider){
         counter = 1;
      }
   },3000);

   setInterval(() => {
      area_id.forEach((areaId) => callAPI(areaId))
   }, 7200000);

   $("#status-filter").change(async function (e) {
      areaName = []
      last_slider = 0;
      $(".ring").removeClass("d-none")
      await callAPIwithFilter($(this).val())
      counter = 1;
   })
})

async function generateCard(data,area,jml_mp) {
   let counter = 0,
      batch = 0;
   Object.values(data).forEach(function (o) {
      var nama = o.nama, accel = o.accel, velocity = o.velocity, temp = o.temp, status = o.status, dna12 = o.dna12, dna500 = o.dna500 , updated = new Date(o.last_update);
      var content = `<p class="mb-0"> Velocity : <b>${velocity.toPrecision(3)}</b> mm/s (RMS)</p>
      <p class="mb-0"> Temperature : <b>${temp.toPrecision(3)}</b> <sup>o</sup>C</p>`;
      var warnaTxt = "";
      
      if (status != 2) {
         if (status == 0)
            warnaTxt = "text-white";

         content = `<p class="mb-0 ${warnaTxt}"> Velocity : <b>${velocity.toPrecision(3)}</b> mm/s (RMS)</p>
                     <p class="mb-0 ${warnaTxt}"> Acceleration : <b>${accel.toPrecision(3)}</b> g (pk)</p>
                     <p class="mb-0 ${warnaTxt}"> Temperature : <b>${temp.toPrecision(3)}</b> <sup>o</sup>C </p>`;
      }
      
      if (dna12 > 0 || dna500 > 0) {
         if (status == 0)
            warnaTxt = "text-white";
            
         content = `<p class="mb-0 ${warnaTxt}"> DNA12 g : <b>${dna12.toPrecision(3)}</b> pk-pk </p>
                     <p class="mb-0 ${warnaTxt}"> DNA500 g : <b>${accel.toPrecision(4)}</b> pk-pk </p>`;
      }
      switch (status) {
         case 1:
            status = WARNING;
            break;
         case 0:
            status = ERROR;
            break;
         default:
            status = NORMAL;
            break;
      }

      const card = `<div class="col-lg-2 col-6">
                  <div class="small-box ${status} opacity-25">
                     <div class="inner opacity-125">
                        <h5 class="${warnaTxt}" >${nama}</h5>
                        ${content}
                     </div>
                     <div  class="small-box-footer">Update: ${updated.toLocaleDateString('en-GB')} ${updated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</div>
                  </div>
               </div>`;
      counter++;

      if (counter == 15) {
         counter -= counter;
         batch++;
      }

      $(`#${area+batch}`).append(card);
   })
}

function generateButton(nomer) {
   $("#container").append(`<input type="radio" name="radio-btn" id="radio${nomer}">`);
   $(".navigation-auto").append(`<div class="auto-btn${nomer}"></div>`)
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
            
         const content = `<div class="slide ${area_name}">
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
      
      last_slider += batch
      $(".slide").first().addClass("first")
      await generateCard(data,area_name,jml_mp);
   });
}

async function callAPIwithFilter(filter) {
   let firstContent = `
            <!-- Radio Button Start-->
            <input type="radio" name="radio-btn" id="radio1">
            <input type="radio" name="radio-btn" id="radio2">
            <input type="radio" name="radio-btn" id="radio3">
            <input type="radio" name="radio-btn" id="radio4">
            <input type="radio" name="radio-btn" id="radio5">
            <input type="radio" name="radio-btn" id="radio6">
            <input type="radio" name="radio-btn" id="radio7">
            <input type="radio" name="radio-btn" id="radio8">
            <input type="radio" name="radio-btn" id="radio9">
            <input type="radio" name="radio-btn" id="radio10">
            <input type="radio" name="radio-btn" id="radio11">
            <input type="radio" name="radio-btn" id="radio12">
            <input type="radio" name="radio-btn" id="radio13">
            <input type="radio" name="radio-btn" id="radio14">
            <input type="radio" name="radio-btn" id="radio15">
            <input type="radio" name="radio-btn" id="radio16">
            <input type="radio" name="radio-btn" id="radio17">
            <input type="radio" name="radio-btn" id="radio18">
            <!-- Radio Button End-->
            
            <!-- Automatic Navigation Start-->
            <div class="navigation-auto">
               <div class="auto-btn1"></div>
               <div class="auto-btn2"></div>
               <div class="auto-btn3"></div>
               <div class="auto-btn4"></div>
               <div class="auto-btn5"></div>
               <div class="auto-btn6"></div>
               <div class="auto-btn7"></div>
               <div class="auto-btn8"></div>
               <div class="auto-btn9"></div>
               <div class="auto-btn10"></div>
               <div class="auto-btn11"></div>
               <div class="auto-btn12"></div>
               <div class="auto-btn13"></div>
               <div class="auto-btn14"></div>
               <div class="auto-btn15"></div>
               <div class="auto-btn16"></div>
               <div class="auto-btn17"></div>
               <div class="auto-btn18"></div>
            </div>
            <!-- Automatic Navigation End-->`;
   $("#container").html(firstContent);
   const areasId = [1,2,3,4,5]
   areasId.forEach((id) => {
      $.get("/dashboard/v1?area=" + id + "&status=" + filter, async function (o) {
         var area_name = o.data.area_name, jml_mp = o.data.jumlah,
            batch = jml_mp > 15 ? Math.floor(jml_mp / 15) : 1,
            remains = jml_mp % 15, 
            data = o.data.measure_points;

         for (let index = 0; index < batch; index++) {
            if (remains == 0 && index == batch)
               break;

            const content = `<div class="slide ${area_name}">
                     <div class="content">
                        
                        <div class="m-4">
                           <div class="row" id="${area_name + index}">
                           </div> 
                        </div>
                     </div>
               </div>`;

            $("#container").append(content);
            areaName.push(area_name);
         }
         
         last_slider += batch
         $(".slide").first().addClass("first");
         await generateCard(data, area_name, jml_mp);
      });
      $(".ring").addClass("d-none")
   })
}