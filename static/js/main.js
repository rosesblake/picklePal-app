((g) => {
  var h,
    a,
    k,
    p = "The Google Maps JavaScript API",
    c = "google",
    l = "importLibrary",
    q = "__ib__",
    m = document,
    b = window;
  b = b[c] || (b[c] = {});
  var d = b.maps || (b.maps = {}),
    r = new Set(),
    e = new URLSearchParams(),
    u = () =>
      h ||
      (h = new Promise(async (f, n) => {
        await (a = m.createElement("script"));
        e.set("libraries", [...r] + "");
        for (k in g)
          e.set(
            k.replace(/[A-Z]/g, (t) => "_" + t[0].toLowerCase()),
            g[k]
          );
        e.set("callback", c + ".maps." + q);
        a.src = `https://maps.${c}apis.com/maps/api/js?` + e;
        d[q] = f;
        a.onerror = () => (h = n(Error(p + " could not load.")));
        a.nonce = m.querySelector("script[nonce]")?.nonce || "";
        m.head.append(a);
      }));
  d[l]
    ? console.warn(p + " only loads once. Ignoring:", g)
    : (d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n)));
})({
  key: `${apiKey}`, // Ensure apiKey is correctly set
  v: "weekly",
  // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
  // Add other bootstrap parameters as needed, using camel case.
});

let currentMarker = null; // Variable to hold the current marker
let map;
let autocomplete;

async function initMap() {
  try {
    const address = `${city}, ${state}, ${zipCode}`;
    const { Map } = await google.maps.importLibrary("maps");
    map = new Map(document.getElementById("map"), {
      center: { lat: 34.0522, lng: -118.2437 }, // Default center if geocode fails
      zoom: 12,
    });
    // Initialize Autocomplete for the input field
    const input = document.getElementById("location-input");
    autocomplete = new google.maps.places.Autocomplete(input);

    // Set up the listener for place selection
    autocomplete.addListener("place_changed", function () {
      const place = autocomplete.getPlace();

      if (!place.geometry) {
        // User entered the name of a Place that was not suggested and pressed the Enter key
        console.log("No details available for input: '" + place.name + "'");
        return;
      }

      // Center the map on the selected place and add a marker
      if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport);
      } else {
        map.setCenter(place.geometry.location);
        map.setZoom(15); // Set the zoom level
      }

      // Add a marker at the selected place
      new google.maps.Marker({
        map: map,
        position: place.geometry.location,
      });
    });

    let geocoder = new google.maps.Geocoder();

    // Geocode the initial address to center the map
    geocoder.geocode({ address: address }, function (results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        let location = results[0].geometry.location;
        map.setCenter(location);
        addMarker(map, location, "Your Location");
      } else {
        console.error(
          "Geocode was not successful for the following reason: " + status
        );
      }
    });

    // Listen for form submission to update map location
    document
      .getElementById("search-form")
      .addEventListener("submit", function (event) {
        event.preventDefault();
        const searchAddress = document.getElementById("location-input").value;
        geocodeAddress(geocoder, map, searchAddress);
      });
  } catch (error) {
    console.error("Error initializing map: ", error);
  }
}

function geocodeAddress(geocoder, map, address) {
  geocoder.geocode({ address: address }, function (results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      let location = results[0].geometry.location;
      map.setCenter(location);
      addMarker(map, location, "Search Result");
      updateAddressBar(location);
    } else {
      console.error(
        "Geocode was not successful for the following reason: " + status
      );
    }
  });
}

function addMarker(map, location, title) {
  try {
    // Remove the previous marker if it exists
    if (currentMarker) {
      currentMarker.setMap(null);
    }

    // Add a new marker
    currentMarker = new google.maps.Marker({
      position: location,
      map: map,
      title: title,
    });
  } catch (error) {
    console.error("Error adding marker: ", error);
  }
}

// function updateAddressBar(location) {
//   let geocoder = new google.maps.Geocoder();

//   // Reverse geocode the marker's location
//   geocoder.geocode({ location: location }, function (results, status) {
//     if (status === google.maps.GeocoderStatus.OK) {
//       if (results[0]) {
//         let address = results[0].formatted_address;
//         // Update the address bar in your HTML
//         document.getElementById("address-bar").innerText = address;
//       } else {
//         console.log("No results found");
//       }
//     } else {
//       console.log("Geocoder failed due to: " + status);
//     }
//   });
// }
