document.addEventListener("DOMContentLoaded", function () {
  const citySelect = document.getElementById("city");
  const districtSelect = document.getElementById("district");
  const wardSelect = document.getElementById("ward");

  if (!citySelect || !districtSelect || !wardSelect) return;

  const currentCity = citySelect.dataset.current || "";
  const currentDistrict = districtSelect.dataset.current || "";
  const currentWard = wardSelect.dataset.current || "";

  // Load tỉnh
  fetch("https://provinces.open-api.vn/api/p/")
    .then(res => res.json())
    .then(data => {
      data.forEach(city => {
        const selected = city.name === currentCity ? "selected" : "";
        citySelect.innerHTML += `
          <option value="${city.name}" data-code="${city.code}" ${selected}>
            ${city.name}
          </option>`;
      });

      if (currentCity) {
        loadDistrict(citySelect.selectedOptions[0].dataset.code);
      }
    });

  function loadDistrict(cityCode) {
    districtSelect.disabled = true;
    fetch(`https://provinces.open-api.vn/api/p/${cityCode}?depth=2`)
      .then(res => res.json())
      .then(data => {
        districtSelect.innerHTML = '<option value="">Chọn quận / huyện</option>';
        data.districts.forEach(d => {
          const selected = d.name === currentDistrict ? "selected" : "";
          districtSelect.innerHTML += `
            <option value="${d.name}" data-code="${d.code}" ${selected}>
              ${d.name}
            </option>`;
        });
        districtSelect.disabled = false;

        if (currentDistrict) {
          loadWard(districtSelect.selectedOptions[0].dataset.code);
        }
      });
  }

  function loadWard(districtCode) {
    wardSelect.disabled = true;
    fetch(`https://provinces.open-api.vn/api/d/${districtCode}?depth=2`)
      .then(res => res.json())
      .then(data => {
        wardSelect.innerHTML = '<option value="">Chọn phường / xã</option>';
        data.wards.forEach(w => {
          const selected = w.name === currentWard ? "selected" : "";
          wardSelect.innerHTML += `
            <option value="${w.name}" ${selected}>${w.name}</option>`;
        });
        wardSelect.disabled = false;
      });
  }

  citySelect.addEventListener("change", function () {
    const code = this.selectedOptions[0].dataset.code;
    loadDistrict(code);
    wardSelect.innerHTML = '<option value="">Chọn phường / xã</option>';
  });

  districtSelect.addEventListener("change", function () {
    const code = this.selectedOptions[0].dataset.code;
    loadWard(code);
  });
});
