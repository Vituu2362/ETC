var app = angular.module("myapp", ['ngCookies']);
app.controller("myappCtrl", function($scope, $cookieStore, $cookies, $http,$filter) 
{
	
/************************** Date Details ***********************************/
			
 $scope.ModifiedDate = $filter("date")(Date.now(), 'yyyy-MM-dd');

 /****************************************************************************/
/************************** Get Admin Details ***********************************/
/****************************************************************************/	
 
 
	$scope.cook_user_email = $cookieStore.get("cook_user_email");
	$scope.cook_user_type = $cookieStore.get("cook_user_type");
	$scope.cook_user_dept = $cookieStore.get("cook_user_dept");			
	$scope.cook_user_mail = $cookieStore.get("cook_user_mail");
	$scope.cook_user_mob = $cookieStore.get("cook_user_mob");
	$scope.cook_user_name = $cookieStore.get("cook_user_name");
	$scope.cook_user_desg = $cookieStore.get("cook_user_desg");
	$scope.cook_user_site = $cookieStore.get("cook_user_site");
	$scope.cook_user_area = $cookieStore.get("cook_user_area");

	$scope.user_logout = function() 
	{
		if(confirm("Are You Sure?"))
		{
			$cookies.cook_user_area = "";
			$cookies.cook_user_site = "";
			$cookies.cook_user_desg = "";
			$cookies.cook_user_name = "";
			$cookies.cook_user_mob = "";
			$cookies.cook_user_mail = "";
			$cookies.cook_user_email = "";
			$cookies.cook_admin_email="";
			$cookies.cook_user_type = "";
			$cookies.cook_user_dept = "";
			window.location = "index.html";
			return;
		}
		else
		{
			return false;
		}
	}
	

/****************************************************************************/
/************************Home page*********************************
/****************************************************************************/
	if(!$cookies.cook_user_email)
	{
		$scope.UserHomeVar = false; //hide
		$scope.HomeVar = true; //hide
	}
	else 
	{
		$scope.UserHomeVar = true; //show
		$scope.HomeVar = false; //hide
	}

/****************************************************************************/
/************************** Get My Survey ***********************************/
/****************************************************************************/

		
	$http.post('get_all_toll.php')
		.success(function(data, status, headers, config) 
		{
			$scope.all_bus_details = data.details;
        });
		
	$http.post('get_date.php')
	.success(function(data, status, headers, config) 
	{
		$scope.date_details = data.details;
	});
	
	$http.post('get_user_ticket_last.php', 
		{
		'id':$scope.cook_user_email
		})
		.success(function(data, status, headers, config) 
		{
			$scope.user_ticket_details = data.details;
        });
		
	$http.post('get_all_ticket.php', 
		{
		'id':$scope.cook_user_email
		})
		.success(function(data, status, headers, config) 
		{
			$scope.all_ticket_details = data.details;
        });
		
	$http.post('get_user_toll.php', 
		{
		'id':$scope.cook_user_mail
		})
		.success(function(data, status, headers, config) 
		{
			$scope.user_grievance_details = data.details;
        });
		
	$http.post('get_user_ticket.php', 
		{
		'id':$scope.cook_user_mail
		})
		.success(function(data, status, headers, config) 
		{
			$scope.user_ticket_details = data.details;
        });
		
	$http.post('get_user_redressal.php', 
		{
		'id':$scope.cook_user_type,'dept':$scope.cook_user_dept
		})
		.success(function(data, status, headers, config) 
		{
			$scope.user_redressal_details = data.details;
        });
		
	$http.post('get_all_redressal.php')
		.success(function(data, status, headers, config) 
		{
			$scope.all_redressal_details = data.details;
        });
		
	$http.post('get_forward.php',{
			'dept':$scope.cook_user_dept,'type':$scope.cook_user_type
		})
		.success(function(data, status, headers, config) 
		{
			$scope.names = data.details;
        });
		
	$http.post('get_category.php')
	.success(function(data, status, headers, config) 
	{
			$scope.category_details = data.details;
	});

/*
$scope.get_file_data = function() 
	{
 $http.get('upload.php')
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("File Responese Successfully");
				window.location = "user_home.html";
				return;				
			}
			else 
			{
				alert("Fill All Fields");
			}
        });
	}
*/

/****************************************************************************/
/************************** create_application **********************************/
/****************************************************************************/
	$scope.field_11="Nil";
	
	$scope.create_application = function() 
	{
		$scope.cook_user_dept_1 ="Nil";
		
		$http.post('create_application.php', 
		{
		'field_1':$scope.ModifiedDate,'field_2':$scope.field_2,
		'field_3':$scope.cook_user_email,'field_4':$scope.cook_user_name,
		'site':$scope.cook_user_site,'area':$scope.cook_user_area,
		'type':$scope.cook_user_type,
		'field_5':$scope.cook_user_dept_1,'field_6':$scope.cook_user_mob,
		'field_7':$scope.cook_user_mail,'field_8':$scope.cook_user_desg,
		'field_9':$scope.field_9,'field_10':$scope.field_10,
		'field_11':$scope.field_11,'field_12':$scope.field_12
		})
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Created Successfully");
				window.location = "my_application.html";
				return;				
			}
			else if(data.success == 2)
			{
				alert("Fill All Fields");
			}
			else if(data.success == 3)
			{
				alert("Fill Min 5 char in Grievance ");
			}
			else if(data.success == 4)
			{
				alert("Mobile must be 10 digits ");
			}
			else
			{
				alert("Fill All Fields");
			}
        });
    }
	
	 
	 

/****************************************************************************/
/************************** Application Get *********************************/
/****************************************************************************/

$scope.user_update_info = function(name,password,mobile) 
	{
		window.location = "user_info_edit.html";
		$cookieStore.put("cook_name",name);
		$cookieStore.put("cook_password",password);
		$cookieStore.put("cook_mobile",mobile);
		return;
	}	
	
	$scope.cook_name = $cookieStore.get("cook_name");
	$scope.cook_password = $cookieStore.get("cook_password");
	$scope.cook_mobile = $cookieStore.get("cook_mobile");

	$scope.save_update_info = function() 
	{		
		$http.post('user_update_info.php',{
		 'name':$scope.cook_name, 'password':$scope.cook_password,
		 'mobile': $scope.cook_mobile, 'email': $scope.cook_user_email})
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Submited successfully");
				window.location = "user_update_info.html";
				return;				
			}
			else
			{
				alert("Invalid Inputs");
			}   
          });
     }

		 
/****************************************************************************/
/************************** Rating User  *********************************/
/****************************************************************************/

	$scope.grievance_rating = function(email) 
	{
		window.location = "user_rating.html";
		$cookieStore.put("cook_email",email);
		return;
	}	
	
	$scope.cook_email = $cookieStore.get("cook_email");

	$scope.save_rating = function() 
	{		
		$http.post('save_rating.php',{
		 'email':$scope.cook_email, 'field_1':$scope.field_1,'field_2':$scope.comment
		 })
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Submited successfully");
				window.location = "user_home.html";
				return;				
			}
			else if(data.success == 2)
			{
				alert("Please Fill All Fields");
			}
			else
			{
				alert("Invalid Inputs");
			}   
          });
     }

/****************************************************************************/
/************************** update_grievance  **********************************/
/****************************************************************************/
		 
	$scope.update_grievance = function(email,field_21) 
	{		
		$http.post('update_grievance.php',{
		 'email':email, 'field_1':field_21
		 })
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Updated successfully");
				window.location = "redressal.html";
				return;				
			}
			else if(data.success == 2)
			{
				alert("Please Fill All Fields");
			}
			else
			{
				alert("Invalid Inputs");
			}   
          });
     }

/****************************************************************************/
/************************** delay_grievance  **********************************/
/****************************************************************************/
		 
	$scope.delay_grievance = function(email,delay) 
	{		
		$http.post('delay_grievance.php',{
		 'email':email, 'field_1':delay
		 })
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Updated successfully");
				window.location = "redressal.html";
				return;				
			}
			else if(data.success == 2)
			{
				alert("Please Fill All Fields");
			}
			else
			{
				alert("Invalid Inputs");
			}   
          });
     }

/****************************************************************************/
/************************** forward_grievance  **********************************/
/****************************************************************************/
		 
	$scope.forward_grievance = function(cus_id,field_9) 
	{		
		$http.post('forward_grievance.php',{
		 'cus_id':cus_id, 'field_1':field_9,
		 'type':$scope.cook_user_type,'dept':$scope.cook_user_dept
		 })
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Forwarded successfully");
				window.location = "redressal.html";
				return;				
			}
			else if(data.success == 2)
			{
				alert("Please Fill All Fields");
			}
			else if(data.success == 3)
			{
				alert("Already Forwarded");
			}
			else
			{
				alert("Invalid Inputs");
			}   
          });
     }

	$scope.cook_cus_id = $cookieStore.get("cook_cus_id");

	$scope.update_location = function() 
	{		
	
		//$scope.get_Latitude = document.getElementById('get_Latitude').value;
		//$scope.get_Longitude = document.getElementById('get_Longitude').value;
		
        $http.post('update_location.php', 
			{	
			'field_1': $scope.field_1, 'field_2':$scope.field_2,
			'email':$scope.cook_cus_id
			})
		.success(function(data, status, headers, config) 
		{
			if(data.success == 1)
			{
				alert("Updated Successful");
				window.location = "view_toll_geo.html";
				//location.reload(); 
				return;				
			}
			else if(data.success == 2)
			{
				alert("Please Fill All Fields");
			}
			else
			{
				alert("Login Unsuccessful");
			}
        });
    }
		 
/*****************************************************************************/
/************************** Update update_employee **************************/
/****************************************************************************/
	$scope.update_renewal = function(cus_id,field_1) 
	{
		
		$cookieStore.put("cook_cus_id",cus_id);
		$cookieStore.put("cook_field_1",field_1);
		window.location = "edit_renewal.html";
		return;
	}
	

	$scope.cook_cus_id = $cookieStore.get("cook_cus_id");
	$scope.cook_field_1 = $cookieStore.get("cook_field_1");
	
	
	$scope.upload_file = function(cus_id) 
	{
		$cookieStore.put("cook_cus_id",cus_id);
		window.location = "file_1.html";
		return;
	}
	

	$scope.cook_cus_id = $cookieStore.get("cook_cus_id");
	
	
	
$scope.save_renewal = function() 
	{
	$http.post('save_renewal.php', 
			{
			'id': $scope.cook_cus_id,'email': $scope.cook_user_mail,
			'field_1': $scope.cook_field_1
			})
	.success(function(data, status, headers, config) 
	{
		if(data.success == 1)
		{
			alert("Updated Successfully");
			window.location = "my_application.html";
			return;
		}
				else if(data.success == 2)
				{
					alert("Adding Unsuccessful");
				}
				else
				{
					alert("Fill All Fields");
				}
			
    });
	}
	
	
	
	
});