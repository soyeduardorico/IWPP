// Function to toggle the visibility of the "side-container" element
function toggleSideContainer() {
    if (sideContainer.style.display === 'none') {
      sideContainer.style.display = 'block';
    } else {
      sideContainer.style.display = 'none';
    }
  }

// Creates an initial list of checkboxes  of zeros list and calls the function to move on
function moveToPage(url1){
  var url2 = url1 + '_register';
  statusInitial = [false, false, false, false, false, false, false, false]
  saveToNext(url1,url2, statusInitial)}

// Reads the checkboxes, saves them into a list and calls the function to move on
function updateSelf(url1){
  var url2 = url1 + '_register';
  var statusList = [];
  for (var i = 1; i <= 8; i++) {
      var checkbox = document.getElementById('status' + i + 'Checkbox');
      if (checkbox) {
          statusList.push(checkbox.checked);
      }
  }
  saveToNext(url1,url2, statusList)}

// Saves the list into a JSON file and moves on to a given page
function saveToNext(url1,url2, statusPass){
var js_data = JSON.stringify(statusPass, null, 2);
$.ajax({
              url: url2,
              type: 'post',
              contentType: 'application/json',
              dataType: 'json',
              data: js_data
          }).done(function(result) {console.log(result)
              window.location.href= url1;})
          }
