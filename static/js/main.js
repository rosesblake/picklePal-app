((g) => {
  const p = "The Google Maps JavaScript API",
    c = "google",
    l = "importLibrary",
    q = "__ib__",
    m = document,
    b = window;

  const bMaps = b[c] || (b[c] = {}).maps || (b[c].maps = {});
  const r = new Set();
  const e = new URLSearchParams();

  const u = () =>
    h ||
    (h = new Promise(async (f, n) => {
      const a = m.createElement("script");
      e.set("libraries", [...r] + "");
      Object.keys(g).forEach((k) =>
        e.set(
          k.replace(/[A-Z]/g, (t) => "_" + t[0].toLowerCase()),
          g[k]
        )
      );
      e.set("callback", c + ".maps." + q);
      a.src = `https://maps.${c}apis.com/maps/api/js?` + e;
      bMaps[q] = f;
      a.onerror = () => (h = n(Error(p + " could not load.")));
      a.nonce = m.querySelector("script[nonce]")?.nonce || "";
      m.head.append(a);
    }));

  if (!bMaps[l]) {
    bMaps[l] = (f, ...n) => {
      r.add(f);
      u().then(() => bMaps[l](f, ...n));
    };
  } else {
    console.warn(p + " only loads once. Ignoring:", g);
  }
})({
  key: `${apiKey}`, // Ensure apiKey is correctly set
  v: "weekly",
  // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
  // Add other bootstrap parameters as needed, using camel case.
});

let currentMarker = null; // Variable to hold the current marker
let map;
let infoWindow;

async function initMap() {
  try {
    const { Map } = await google.maps.importLibrary("maps");
    map = new Map(document.getElementById("map"), {
      center: { lat: 34.0522, lng: -118.2437 }, // Default center if no courts are available
      zoom: 11,
    });

    // Add markers for each court
    courtsData.forEach((court) => {
      addMarker(
        map,
        { lat: court.latitude, lng: court.longitude },
        court.name,
        court.address,
        court.court_image,
        court.id
      );
    });

    // Initialize Autocomplete for the input field if needed
    const input = document.getElementById("location-input");
    if (input) {
      const autocomplete = new google.maps.places.Autocomplete(input);
      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (place.geometry) {
          if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
          } else {
            map.setCenter(place.geometry.location);
            map.setZoom(15);
          }
        } else {
          console.log("No details available for input: '" + place.name + "'");
        }
      });
    }

    const geocoder = new google.maps.Geocoder();
    infoWindow = new google.maps.InfoWindow();

    // Listen for clicks on the map to possibly add new courts
    map.addListener("click", (e) => {
      const clickedLocation = e.latLng;
      const service = new google.maps.places.PlacesService(map);

      // Reverse geocode the clicked location to get the place details
      geocoder.geocode({ location: clickedLocation }, (results, status) => {
        if (status === google.maps.GeocoderStatus.OK && results[0]) {
          const placeId = results[0].place_id;
          if (placeId) {
            // Get detailed place information using the place ID
            service.getDetails({ placeId: placeId }, (place, status) => {
              if (status === google.maps.places.PlacesServiceStatus.OK) {
                const address = place.formatted_address;
                const photos = place.photos;
                const placeName = place.name;
                const photoUrl =
                  photos && photos.length > 0
                    ? photos[0].getUrl({ maxWidth: 200, maxHeight: 200 })
                    : "";

                const contentString = `
                  <div>
                    <h1 class="text-xl"><strong>${placeName}</strong></h1>
                    ${
                      photoUrl
                        ? `<img src="${photoUrl}" alt="${placeName}" class="w-full h-auto mb-2" />`
                        : ""
                    }
                    <p>${address}</p>
                    <form action="/courts" method="post" style="display: inline;">
                      <input type="hidden" name="csrf_token" value="${csrfToken}">   
                      <input type="hidden" name="name" value="${placeName}">
                      <input type="hidden" name="address" value="${address}">
                      <input type="hidden" name="latitude" value="${clickedLocation.lat()}">
                      <input type="hidden" name="longitude" value="${clickedLocation.lng()}">
                      <input type="hidden" name="court_image" value="${photoUrl}">
                      <button type="submit" class="underline cursor-pointer text-blue-500" style="color: #3b82f6 !important;">
                        Add New Court
                      </button>
                    </form>
                  </div>
                `;

                // Set the position and content of the InfoWindow
                infoWindow.setPosition(clickedLocation);
                infoWindow.setContent(contentString);
                infoWindow.open(map);
              }
            });
          }
        }
      });
    });

    // Optional: Geocode an initial address if needed
    const initialAddress = `${city}, ${state}, ${zipCode}`;
    geocoder.geocode({ address: initialAddress }, (results, status) => {
      if (status === google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
      } else {
        console.error(
          "Geocode was not successful for the following reason: " + status
        );
      }
    });
  } catch (error) {
    console.error("Error initializing map: ", error);
  }
}

function addMarker(map, location, name, address, courtImage, courtId) {
  try {
    const marker = new google.maps.Marker({
      position: location,
      map: map,
      title: name,
      icon: {
        url: "static/images/custom-marker.png", // Custom marker for courts
        scaledSize: new google.maps.Size(39, 60),
      },
    });
    // show court details when custom pin is clicked
    marker.addListener("click", () => {
      const courtUrl = `/courts/${courtId}`;
      const mapsUrl = `https://www.google.com/maps?q=${location.lat},${location.lng}`;
      const contentString = `
        <div>
          <a href="${courtUrl}" class="underline cursor-pointer text-blue-500" style="color: #3b82f6 !important;"><h1 class="text-xl"><strong>${name}</strong></h1>
          <img src="${courtImage} alt=${name} image" class="w-full h-auto mb-2"/>
          </a>
          <p>${address}</p>
          <a href="${mapsUrl}" target="_blank" class="underline cursor-pointer text-blue-500" style="color: #3b82f6 !important;">
            Show on Google Maps
          </a>
          <br>
          <a href="${courtUrl}" class="underline cursor-pointer text-blue-500" style="color: #3b82f6 !important;">Court Information<a/>
        </div>
      `;

      infoWindow.setPosition(location);
      infoWindow.setContent(contentString);
      infoWindow.open(map);
    });
  } catch (error) {
    console.error("Error adding marker: ", error);
  }
}
