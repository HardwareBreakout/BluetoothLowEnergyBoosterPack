package com.hardwarebreakout.bleboosterdemo;

import android.app.Fragment;
import android.os.Bundle;
import android.text.Html;
import android.text.method.LinkMovementMethod;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

public class HomeFragment extends Fragment {
	
	private final String home = "<h2>Welcome to the BLE Booster Demo Application!</h2>" +
			"<p>This is the demo application for the BLE Booster " + 
			" from the Hardware Breakout Store. This board" +
			" can be purchased online at:</p>" +
			"</p><a href=\"http://store.hardwarebreakout.com\"" +
			">http://store.hardwarebreakout.com<\\a>.<\\p>" +
			"<p>Please use the sidebar to navigate this application.</p>";
	
	@Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
        Bundle savedInstanceState) {
		super.onCreateView(inflater, container, savedInstanceState);

        // Inflate the layout for this fragment
		View v = inflater.inflate(R.layout.fragment_home, container, false);
		
        TextView homeText = (TextView) v.findViewById(R.id.home_text);
        homeText.setText(Html.fromHtml(home));
        homeText.setMovementMethod(LinkMovementMethod.getInstance());
		
        return v;
    }
}
