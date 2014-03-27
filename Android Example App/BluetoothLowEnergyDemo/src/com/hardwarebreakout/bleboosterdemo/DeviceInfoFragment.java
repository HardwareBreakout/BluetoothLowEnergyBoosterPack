package com.hardwarebreakout.bleboosterdemo;

import java.text.DecimalFormat;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;

public class DeviceInfoFragment extends BleFragment implements OnClickListener {
    private final static String TAG = DeviceInfoFragment.class.getSimpleName();
    
    private int MODE = 0;
    private double VCC = 2.1;

    private static final int MEASURE_VCC = 1;
    private static final int MEASURE_V_BATTERY = 2;
    private static final int MEASURE_TEMP = 3;


	@Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
        Bundle savedInstanceState) {
		super.onCreateView(inflater, container, savedInstanceState);
		
        // Inflate the layout for this fragment
		View v = inflater.inflate(R.layout.fragment_device_info_demo, container, false);

        Button vccButton = (Button) v.findViewById(R.id.update_VCC_button_id);
        vccButton.setOnClickListener(this);

        Button batteryButton = (Button) v.findViewById(R.id.update_V_battery_button_id);
        batteryButton.setOnClickListener(this);

        Button temperatureButton = (Button) v.findViewById(R.id.update_temperature_button_id);
        temperatureButton.setOnClickListener(this);
    
		Spinner spinner = (Spinner) v.findViewById(R.id.device_spinner_id);
		// Create an ArrayAdapter using the string array and a default spinner layout
		ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(getActivity(),
				R.array.device_spinner_array, android.R.layout.simple_spinner_item);
		// Specify the layout to use when the list of choices appears
		adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		// Apply the adapter to the spinner
		spinner.setAdapter(adapter);
		
		return v;
	}
	
	@Override
    public void onClick(View v) {
        Log.d(TAG, "onClick()" + v.getId());
        switch (v.getId()) {
	        case R.id.update_VCC_button_id:
	        	measureVCC(v);
	            break;
	        case R.id.update_V_battery_button_id:
	        	measureBatteryV(v);
	            break;
	        case R.id.update_temperature_button_id:
	        	measureTemperature(v);
	            break;
        }
    }
	
	public void measureVCC(View view) {
    	MODE = MEASURE_VCC;
		sendData(new byte[] {'4'});
	}
	public void measureBatteryV(View view) {
    	MODE = MEASURE_V_BATTERY;
		sendData(new byte[] {'6'});
	}
	public void measureTemperature(View view) {
    	MODE = MEASURE_TEMP;
		sendData(new byte[] {'5'});
	}
			
	public void updateVCC(double vcc) {
		EditText buttonCount = (EditText) getView().findViewById(R.id.VCC_value_id);
        DecimalFormat df = new DecimalFormat("#.##");
		buttonCount.setText(df.format(vcc)+" V");
	}
	
	public void updateBatteryV(double batteryV) {
		EditText buttonCount = (EditText) getView().findViewById(R.id.V_battery_value_id);
        DecimalFormat df = new DecimalFormat("#.##");
		buttonCount.setText(df.format(batteryV)+" V");
	}
	
	public void updateTemperature(double temperature) {
		EditText buttonCount = (EditText) getView().findViewById(R.id.temperature_value_id);
        DecimalFormat df = new DecimalFormat("#.##");
		buttonCount.setText(df.format(temperature) + " °F");
	}
	
    public void dataReceived(byte[] data) {    	
    	for (int i = 0; i < data.length; i++) {
			Log.d(TAG, String.format("Raw data: %d", data[i]));
			if (MODE == MEASURE_VCC) {
				updateVCC(((int)data[i]&0xff)/255.0*1.5*2.0);
				MODE = 0;
			}
			else if (MODE == MEASURE_V_BATTERY) {
				updateBatteryV(((int)data[i]&0xff)/255.0*VCC*2);
				MODE = 0;
			}
			else if (MODE == MEASURE_TEMP) {
				// First convert to voltage
				double temperature = ((int)data[i]&0xff)/255.0*1.5;
				
				Spinner spinner = (Spinner) getView().findViewById(R.id.device_spinner_id);
				String device = spinner.getSelectedItem().toString();
				if (device.equals("MSP430G2553")) {
					// Then convert to C
					temperature = (temperature-0.986)/0.00355;
				}
				else if (device.equals("MSP430F5529")) {
					// Then convert to C
					temperature = (temperature-0.680)/0.00225;
				}
				// Finally convert to F
				updateTemperature((temperature*9.0/5.0)+32.0);
				MODE = 0;
			}
    	}
    }
}
