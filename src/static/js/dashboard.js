const WARNING = "warning";
const NORMAL = "success";
const ERROR = "danger";
const btn = ``;

var areaName = [];
let last_slider = 0,
  nomer = 0;
$(document).ready(function () {
  let counter = 1;
  const area_id = [1, 2, 3, 4, 5];

  setTimeout(() => {
    area_id.forEach(async (areaId) => {
      await callAPI(areaId);
      $(".ring").addClass("d-none");
    });
  }, 2000);

  let toggleSlide = false;
  $(".toggle").click(function (e) {
    e.preventDefault();
    $(this).toggleClass("toggle-on");

    const totalButton = document.querySelectorAll(".radioIndicator");
    const totalSlide = document.querySelectorAll(".carousel-item");

    let currentIndex = 0;
    toggleSlide = !toggleSlide;

    // Menambahkan event listener click pada setiap elemen totalButton
    totalButton.forEach((element, index) => {
      element.addEventListener("click", () => {
        // Menggunakan index untuk menunjukkan elemen yang diklik
        currentIndex = index;

        // Menghentikan interval slide jika ada
        if (toggleSlide === false) {
          clearInterval(slide);
        }

        // Memperbarui tampilan sesuai dengan elemen yang diklik
        $("#area_name").html(areaName[currentIndex]);

        totalButton.forEach((el) => {
          el.classList.remove("active");
        });
        totalSlide.forEach((el) => {
          el.classList.remove("active");
        });

        totalButton[currentIndex].classList.add("active");
        totalSlide[currentIndex].classList.add("active");


      });
    });

    let slide;

    // Perform Slide
    function slideStart(currentIndex) {
      slide = setInterval(() => {
        $("#area_name").html(areaName[currentIndex]);

        totalButton.forEach((element) => {
          element.classList.remove("active");
        });
        totalSlide.forEach((element) => {
          element.classList.remove("active");
        });

        totalButton[currentIndex].classList.add("active");
        totalSlide[currentIndex].classList.add("active");

        currentIndex = (currentIndex + 1) % totalButton.length;
      }, 5000);
    }

    if (toggleSlide === false) {
      clearInterval(slide);
    } else {
      slideStart(currentIndex);
    }
  });

  // reload page
  setInterval(() => {
    document.location.reload();
  }, 4500000);

  $("#status-filter").change(async function (e) {
    areaName = [];
    last_slider = 0;
    $(".ring").removeClass("d-none");
    await callAPIwithFilter($(this).val());
    counter = 1;
  });
});

async function generateCard(data, area, jml_mp) {
  let counter = 0,
    batch = 0;
  Object.values(data).forEach(function (o) {
    var nama = o.nama,
      accel = o.accel,
      velocity = o.velocity,
      temp = o.temp,
      status = o.status,
      dna12 = o.dna12,
      dna500 = o.dna500,
      updated = new Date(o.last_update);
    var content = `<p class="mb-0"> Velocity : <b>${velocity.toPrecision(
      3
    )}</b> mm/s (RMS)</p>
      <p class="mb-0"> Temperature : <b>${temp.toPrecision(
        3
      )}</b> <sup>o</sup>C</p>`;
    var warnaTxt = "";

    if (temp == 0) {
      content = `<p class="mb-0"> Velocity : <b>${velocity.toPrecision(
        3
      )}</b> mm/s (RMS)</p>
            <p class="mb-0"> Temperature : <b>N/A</b></p>`;
    }

    if (status != 2) {
      if (status == 0) warnaTxt = "text-white";

      content = `<p class="mb-0 ${warnaTxt}"> Velocity : <b>${velocity.toPrecision(
        3
      )}</b> mm/s (RMS)</p>
                     <p class="mb-0 ${warnaTxt}"> Acceleration : <b>${accel.toPrecision(
        3
      )}</b> g (pk)</p>
                     <p class="mb-0 ${warnaTxt}"> Temperature : <b>${temp.toPrecision(
        3
      )}</b> <sup>o</sup>C </p>`;

      if (temp == 0) {
        content = `<p class="mb-0 ${warnaTxt}"> Velocity : <b>${velocity.toPrecision(
          3
        )}</b> mm/s (RMS)</p>
                     <p class="mb-0 ${warnaTxt}"> Acceleration : <b>${accel.toPrecision(
          3
        )}</b> g (pk)</p>
                     <p class="mb-0 ${warnaTxt}"> Temperature : <b> N/A </b> </p>`;
      }
    }

    if (dna12 > 0 || dna500 > 0) {
      if (status == 0) warnaTxt = "text-white";

      content = `<p class="mb-0 ${warnaTxt}"> DNA12 g : <b>${dna12.toPrecision(
        3
      )}</b> pk-pk </p>
                     <p class="mb-0 ${warnaTxt}"> DNA500 g : <b>${accel.toPrecision(
        4
      )}</b> pk-pk </p>`;
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
                        <h5 class="${warnaTxt} font-weight-bold" >${nama}</h5>
                        ${content}
                     </div>
                     <div  class="small-box-footer">${updated.toLocaleString(
                       "en-GB",
                       {
                         hour12: false,
                       }
                     )}</div>
                  </div>
               </div>`;
    counter++;

    if (counter == 15) {
      counter -= counter;
      batch++;
    }

    $(`#${area + batch}`).append(card);
  });
}

function generateButton(nomer) {
  $(".carousel-indicators").append(
    `<button
            class="radioIndicator"
            type="button"
            data-bs-target="#carouselExampleIndicators"
            data-bs-slide-to="${nomer}"
            aria-current="true"
            aria-label="Slide 1"></button>`
  );
}

async function callAPI(areaId) {
  $.get("/dashboard/v1?area=" + areaId, async function (o) {
    var area_name = o.data.area_name,
      jml_mp = o.data.jumlah,
      batch = Math.floor(jml_mp / 15),
      remains = jml_mp % 15,
      data = o.data.measure_points;

    for (let index = 0; index < batch; index++) {
      if (remains == 0 && index == batch) break;

      // const content2 = `<div class="slide ${area_name}">
      //          <div class="content">

      //             <div class="m-4">
      //                <div class="row" id="${area_name+index}">
      //                </div>
      //             </div>
      //          </div>
      //    </div>`;

      const content = `
            <div class="carousel-item  ${areaId} animate__animated animate__bounceInRight">
            <div class="d-block vh-75">
              <div class="card">
                <div class="card-body">
                  <div class="row" id="${area_name + index}"></div>
                </div>
              </div>
            </div>
          </div>`;

      $("#container").append(content);
      generateButton(nomer);
      nomer++;

      areaName.push(area_name);
    }

    last_slider += batch;
    $(".carousel-item").first().addClass("active");
    $(".radioIndicator").first().addClass("active");
    await generateCard(data, area_name, jml_mp);
  });
}

// async function callAPIwithFilter(filter) {
//   let firstContent = `
//             <!-- Radio Button Start-->
//             <input type="radio" name="radio-btn" id="radio1">
//             <input type="radio" name="radio-btn" id="radio2">
//             <input type="radio" name="radio-btn" id="radio3">
//             <input type="radio" name="radio-btn" id="radio4">
//             <input type="radio" name="radio-btn" id="radio5">
//             <input type="radio" name="radio-btn" id="radio6">
//             <input type="radio" name="radio-btn" id="radio7">
//             <input type="radio" name="radio-btn" id="radio8">
//             <input type="radio" name="radio-btn" id="radio9">
//             <input type="radio" name="radio-btn" id="radio10">
//             <input type="radio" name="radio-btn" id="radio11">
//             <input type="radio" name="radio-btn" id="radio12">
//             <input type="radio" name="radio-btn" id="radio13">
//             <!-- Radio Button End-->

//             <!-- Automatic Navigation Start-->
//             <div class="navigation-auto">
//                <div class="auto-btn1"></div>
//                <div class="auto-btn2"></div>
//                <div class="auto-btn3"></div>
//                <div class="auto-btn4"></div>
//                <div class="auto-btn5"></div>
//                <div class="auto-btn6"></div>
//                <div class="auto-btn7"></div>
//                <div class="auto-btn8"></div>
//                <div class="auto-btn9"></div>
//                <div class="auto-btn10"></div>
//                <div class="auto-btn11"></div>
//                <div class="auto-btn12"></div>
//                <div class="auto-btn13"></div>

//             </div>
//             <!-- Automatic Navigation End-->`;
//   $("#container").html(firstContent);
//   const areasId = [1, 2, 3, 4, 5];
//   areasId.forEach((id) => {
//     $.get("/dashboard/v1?area=" + id + "&status=" + filter, async function (o) {
//       var area_name = o.data.area_name,
//         jml_mp = o.data.jumlah,
//         batch = jml_mp > 15 ? Math.floor(jml_mp / 15) : 1,
//         remains = jml_mp % 15,
//         data = o.data.measure_points;

//       for (let index = 0; index < batch; index++) {
//         if (remains == 0 && index == batch) break;

//         const content = `<div class="slide ${area_name}">
//                      <div class="content">

//                         <div class="m-4">
//                            <div class="row" id="${area_name + index}">
//                            </div>
//                         </div>
//                      </div>
//                </div>`;

//         $("#container").append(content);
//         areaName.push(area_name);
//       }

//       last_slider += batch;
//       $(".slide").first().addClass("first");
//       await generateCard(data, area_name, jml_mp);
//     });
//     $(".ring").addClass("d-none");
//   });
// }
