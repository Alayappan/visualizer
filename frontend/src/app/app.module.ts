/**
 * App module
 */
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AppComponent } from './app.component';
import { FileUploadComponent } from './components/file-upload.component';
import { GraphViewerComponent } from './components/graph-viewer.component';
import { DetailPanelComponent } from './components/detail-panel.component';
import { GraphService } from './services/graph.service';

@NgModule({
    declarations: [
        AppComponent,
        FileUploadComponent,
        GraphViewerComponent,
        DetailPanelComponent
    ],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        HttpClientModule,
        FormsModule,
        CommonModule
    ],
    providers: [GraphService],
    bootstrap: [AppComponent]
})
export class AppModule { }
