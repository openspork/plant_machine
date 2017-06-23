$(document).ready(function() {          
    $('button').each(function(){
        $(this).click(function(){
            instr = $(this).attr('id').replace(/_/g , '/')

            instr_split = instr.split("/")

            op = instr_split[0]
            mod = instr_split[1]

           	switch (op){
           		case "add":
           			switch (mod){
           				case "hwg":
           					$.post (instr, { 
           						name: $('#add_hwg_name').val() 
           					})
           					break
           				case "sth": 
           					$.post (instr, { 
           						name: $('#add_sth_name').val(),
           					addr: $('#add_sth_addr').val() 
           					})
           					break
           				case "shy":
           					$.post (instr, {
           						name: $('#add_shy_name').val(),
           						port: $('#add_shy_port').val(), 
           						dev: $('#add_shy_dev').val(),
           						chan: $('#add_shy_chan').val()
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
           			break //break from "add" case
           		case "ass":
           			
           		case "rem":
           		case "del":
           			$.post(instr)
           			break // break from "rem", "del" cases
        	}
            location.reload();
        });
    });
});