function BasicLineChart(strTitle,strYTitle,arrX,arrY,strTooltip,arrData){
	var title={
		text:strTitle
	};
	
	var subtitle={
		text: ''
	};
	
	var xAxis={
		title:{
			text:''
		},		
		labels:{
			style:{
				align:'center',
				fontSize:'10px',
				maxStaggerLines:1		
			}
		},
		categories:arrX
	};	
	
	var yAxis={
		title:{
			text:strYTitle
		},			
		tickPositions:arrY
	};
	
	var legend={
		layout:'vertical',
		align:'right',
		verticalAlign:'middle',
		borderWidth:1
	};
	
	var tooltip={
		valueSuffix:strTooltip
	};
	
	var plotOptions={
		series:{
			lineWidth:2,
			marker:{
				enabled:false
			}			
		}		
	};
	
	var series=arrData;
	
	var credits={
		text:'Copyright@系统测试部',
		href:'',
		position:{
			align:'right',
			x:-20,
			verticalAlign:'bottom',
			y:-5
		},
		style:{
			cursor:'pointer',
			color:'#909090',
			fontSize:'10px'
		}
	};	

	
    var json={};
    json.title=title;
    json.subtitle=subtitle;
    json.xAxis=xAxis;
    json.yAxis=yAxis;
    json.legend=legend;	
    json.tooltip=tooltip;
	json.plotOptions=plotOptions;
    json.series=series;	
    json.credits=credits;
	
	return json;		
}


function Chart(strTitle,arrX,arrY,arrData){
	if (strTitle.indexOf("CPU")>-1){
		var strYTitle="CPU (%)";
	} else{
		var strYTitle="Memory (%)";
	}
	var strTooltip="%";

	var json=BasicLineChart(strTitle,strYTitle,arrX,arrY,strTooltip,arrData);
	
	return json;
}