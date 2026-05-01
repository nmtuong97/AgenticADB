package com.example.aadb_android_sample

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.example.aadb_android_sample.ui.theme.AadbandroidsampleTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AadbandroidsampleTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    AgenticADBTestbed(modifier = Modifier.padding(innerPadding))
                }
            }
        }
    }
}

@Composable
fun AgenticADBTestbed(modifier: Modifier = Modifier) {
    var textValue by remember { mutableStateOf("") }
    var passwordValue by remember { mutableStateOf("") }
    var switchState by remember { mutableStateOf(false) }
    var checkboxState by remember { mutableStateOf(false) }
    var sliderValue by remember { mutableStateOf(0.5f) }
    var isHiddenElementVisible by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "AgenticADB UI Testbed",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.semantics { contentDescription = "Screen Title" }.testTag("title_text")
        )

        // 1. Text Inputs
        OutlinedTextField(
            value = textValue,
            onValueChange = { textValue = it },
            label = { Text("Standard Input") },
            modifier = Modifier.fillMaxWidth().testTag("input_standard")
        )

        OutlinedTextField(
            value = passwordValue,
            onValueChange = { passwordValue = it },
            label = { Text("Password Input") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth().testTag("input_password")
        )

        // 2. Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Button(
                onClick = { /* Action */ },
                modifier = Modifier.testTag("btn_primary").semantics { contentDescription = "Primary Action Button" }
            ) {
                Text("Click Me")
            }

            OutlinedButton(
                onClick = { /* Action */ },
                enabled = false,
                modifier = Modifier.testTag("btn_disabled")
            ) {
                Text("Disabled")
            }
        }

        // 3. Toggles and Sliders
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Switch Option", modifier = Modifier.weight(1f))
            Switch(
                checked = switchState,
                onCheckedChange = { switchState = it },
                modifier = Modifier.testTag("toggle_switch")
            )
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Checkbox Option", modifier = Modifier.weight(1f))
            Checkbox(
                checked = checkboxState,
                onCheckedChange = { checkboxState = it },
                modifier = Modifier.testTag("toggle_checkbox")
            )
        }

        Column {
            Text("Slider: ${sliderValue.times(100).toInt()}%", modifier = Modifier.testTag("slider_text"))
            Slider(
                value = sliderValue,
                onValueChange = { sliderValue = it },
                modifier = Modifier.testTag("slider_component")
            )
        }

        // 4. Nested Layouts & Hidden Elements
        Button(
            onClick = { isHiddenElementVisible = !isHiddenElementVisible },
            modifier = Modifier.fillMaxWidth().testTag("box_toggle_hidden")
        ) {
            Text("Tap to toggle hidden text")
        }

        if (isHiddenElementVisible) {
            Text(
                text = "This is a conditionally rendered text!",
                color = Color.Red,
                modifier = Modifier.testTag("text_hidden")
            )
        }

        // 5. Scrollable Lists
        Text("Horizontal Scroll List:", style = MaterialTheme.typography.titleMedium)
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(10) { index ->
                Card(
                    modifier = Modifier.size(100.dp).testTag("horizontal_item_$index")
                ) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("Item $index")
                    }
                }
            }
        }

        Text("Vertical Scroll Area (Inside Column):", style = MaterialTheme.typography.titleMedium)
        Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(20) { index ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { /* Row click */ }
                            .padding(8.dp)
                            .testTag("vertical_item_$index"),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = if (index % 2 == 0) Icons.Default.Favorite else Icons.Default.Settings,
                            contentDescription = "Item Icon $index",
                            modifier = Modifier.padding(end = 16.dp)
                        )
                        Text("List Element $index")
                    }
                }
            }
        }
    }
}