$(document).ready(function() {

  $("#hw_groups").load("/hw_groups")
  $("#unass_resources").load("/unass_resources")
  $("#add_resources").load("/add_resources")
});

$(document).on("click", "button", function(){
  instr = $(this).attr('id').replace(/_/g , '/')

  instr_split = instr.split("/")

  op = instr_split[0]
  mod = instr_split[1]
  id = instr_split[2]

  switch (op){
    case "add":
      switch (mod){
        case "hwg":
          $.post (instr, { 
            name: $('#add_hwg_name').val(),
            pmp_temp_thresh: $('#add_hwg_pmp_temp_thresh').val(),
            pmp_moist_thresh: $('#add_hwg_pmp_moist_thresh').val(),            
            fan_temp_thresh: $('#add_hwg_fan_temp_thresh').val(),
            fan_moist_thresh: $('#add_hwg_fan_moist_thresh').val()            
          })
          $("#hw_groups").load("/hw_groups")
          break
        case "sth": 
          $.post (instr, { 
            name: $('#add_sth_name').val(),
            addr: $('#add_sth_addr').val(),
          })
          break
        case "shy":
          $.post (instr, {
            name: $('#add_shy_name').val(),
            chan: $('#add_shy_chan').val(),                    
          })
          break
        case "pmp":
            $.post (instr, { 
            name: $('#add_pmp_name').val(),
            pin: $('#add_pmp_pin').val() 
          })
          break
        case "fan":
            $.post (instr, { 
            name: $('#add_fan_name').val(),
            pin: $('#add_fan_pin').val() 
          })
          break                                 
      }
      $("#add_resources").load("/add_resources")
      $("#unass_resources").load("/unass_resources")
      break //break from "add" case
    case "ass":
      $.post(instr, {group: $('#ass_' + mod + '_' + id + '_group').val()})
      $("#hw_groups").load("/hw_groups")
      $("#unass_resources").load("/unass_resources")
      break //break from "add" case                         
    case "rem":
    case "del":
      $.post(instr)
      $("#hw_groups").load("/hw_groups")
      $("#unass_resources").load("/unass_resources")
      break // break from "rem", "del" cases
}
});