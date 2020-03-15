function updatePhotoID(id) {
  var hiddenInput = document.getElementById("photoID");
  hiddenInput.value = id;
  var images = document.querySelectorAll("img");
  images.forEach(image => image.classList.remove("selectedImg"));
  var chosenImg = document.getElementById(id);
  chosenImg.classList.add("selectedImg");
}
