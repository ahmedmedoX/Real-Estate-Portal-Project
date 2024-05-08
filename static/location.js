function codeAddress() {
  getLocation();
}
window.onload = codeAddress;

let v = 0;
        let loc = sessionStorage.getItem("v");

        // For debugging
        // document.getElementById("x").innerHTML = loc;
        
        function getLocation() {
          if (navigator.geolocation && !loc) {
            navigator.geolocation.getCurrentPosition(showPosition);
          }else{
            sessionStorage.setItem("v",loc);
          }
        }
        function showPosition(position) {
            v = position.coords.latitude +' '+ position.coords.longitude;
            sessionStorage.setItem("v",v);
            $(document).ready(function() {
                $.ajax({
                    method: 'GET',
                    url: "{% url 'home' %}",
                    data: {v: v},
                    // success: function (data) {
                    //      //this gets called when server returns an OK response
                    //      alert("it worked!");
                    // },
                    // error: function (data) {
                    //      alert("it didnt work");
                    // }
                });
            });
        }